import data_tools
import pandas as pd


def description_to_df():
    def first_index_of_detail(detail):
        """
        Should be use the wipe out the start of details like '1. we do stuff' or '2- another stuff'
        :return: index in detail where we should start slicing
        """
        def find_index_end_of_seif_number():
            has_seen_non_space = False
            for i, char in enumerate(detail[:-1]):
                if char != ' ':
                    has_seen_non_space = True
                if has_seen_non_space and (char == '-' or char == '.' or char == ' ') and \
                        (ord('9') < ord(detail[i+1]) or ord(detail[i+1]) < ord('0')):
                    return i + 1
            return None
        ind_end_seif = find_index_end_of_seif_number()
        if ind_end_seif is None:
            return 0
        prev_was_revah = False
        for val in detail[:ind_end_seif]:
            if prev_was_revah and ord('א') <= ord(val) <= ord('ת'):
                return 0
            if val == ' ':
                prev_was_revah = True
            else:
                prev_was_revah = False
        return ind_end_seif

    db = data_tools.get_db()
    details = data_tools.get_vals(db, ['PL_NUMBER', 'PL_NAME', 'main_details_from_mavat'])
    details = [data_tools.tup_to_readable_tup(tup) for tup in details]
    split_tups = []
    for tup in details:
        if tup[2] is None:
            continue
        split_details = tup[2].split('<br>')
        for detail in split_details:
            sliced_detail = detail[first_index_of_detail(detail):]
            stripped_detail = sliced_detail.strip()
            if stripped_detail == '':
                continue
            tup_to_insert = (tup[0], tup[1], stripped_detail)
            split_tups.append(tup_to_insert)
    return pd.DataFrame(split_tups, columns=['PL_NUMBER', 'PL_NAME', 'detail'])


def n_relationship(df, n):
    counters_dict = {}
    for i, row in df.iterrows():
        words = [word.strip() for word in row['detail'].split(' ') if word != '']
        for j in range(0, len(words) - (n - 1)):
            n_words = tuple(words[j:j+n])   # because list is not hashable
            if n_words not in counters_dict:
                counters_dict[n_words] = 0
            counters_dict[n_words] += 1
    return counters_dict


if __name__ == '__main__':
    # This will save all the n-relations from 1 to 11 (not included 11)
    df = description_to_df()
    writer = pd.ExcelWriter('../relations.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='original_data')
    for n in range(1, 11):
        relations = sorted(n_relationship(df, n).items(), key=lambda item: item[1], reverse=True)
        relations = [tup for tup in relations if tup[1] > 1]  # don't take combos that do not repeat
        df_n_relation = pd.DataFrame([key + (value,) for key, value in relations],
                                     columns=['word {}'.format(i) for i in range(0, n)] + ['frequency'])
        sheet_name = 'single_words' if n == 1 else '{}_size_relations'.format(n)
        df_n_relation.to_excel(writer, sheet_name=sheet_name)
    writer.save()