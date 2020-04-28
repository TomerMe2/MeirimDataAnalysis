from dataclasses import dataclass
from Classifications.descriptions_to_data import description_to_df
import pandas as pd
import numpy as np

# There's a hebrew words collection that is used in that program:
# https://yeda.cs.technion.ac.il/resources_lexicons_stopwords.html


@dataclass
class BuildingInstruction:
    val: str


@dataclass
class MovementInstruction:
    val: str


@dataclass
class ExpropriationInstruction:
    val: str


@dataclass
class AreaDesignationChangeInstruction:
    val: str
    from_area: str
    to_area: str


@dataclass
class TreesInstruction:
    val: str


@dataclass
class DestructionInstruction:
    val: str


@dataclass
class PermitInstruction:
    val: str


@dataclass
class ArchitecturalInstruction:
    val: str


@dataclass
class StepInstruction:
    val: str


@dataclass
class UnionAndDistributionInstruction:
    val: str


@dataclass
class LandUseInstruction:
    val: str


@dataclass
class PreservationInstruction:
    val: str


def parse_area_designation_change(detail: str, lst_of_heb_words: list):
    curr_word = ''
    gather_word = ''
    from_index = -1
    to_index = -1
    number_of_times_changed_to_index = 0
    for i, curr_char in enumerate(detail):
        if curr_char == ' ' or i == len(detail) - 1:
            curr_word = gather_word
            gather_word = ''

            word_to_search = curr_word.replace(',', '').replace('(', '').replace(')', '')
            if from_index == -1 and curr_word.startswith('מ') and word_to_search not in lst_of_heb_words:
                from_index = i - len(curr_word) + 1
            elif from_index != -1 and curr_word.startswith('ל') and \
                    word_to_search not in lst_of_heb_words:
                # it's < 2 for situation like: דרך להולכי רגל למגורים ב
                if number_of_times_changed_to_index < 2:
                    to_index = i - len(curr_word) + 1
                number_of_times_changed_to_index += 1
        else:
            gather_word = gather_word + curr_char
    if from_index != -1 and to_index != -1 and from_index < to_index:
        from_area = detail[from_index:to_index - 2]
        to_area = detail[to_index:].replace('.', '')
        return AreaDesignationChangeInstruction(detail, from_area, to_area)
    else:
        return AreaDesignationChangeInstruction(detail, '', '')


def parse_detail(detail, lst_of_heb_words):
    if 'הפקעה' in detail or 'הפקעות' in detail:
        return ExpropriationInstruction(detail)
    if 'הנאה' in detail:
        return MovementInstruction(detail)
    if 'שינוי יעוד' in detail or 'שינוי ייעוד' in detail or 'יעוד קרקע' in detail:
        return parse_area_designation_change(detail, lst_of_heb_words)
    if 'שינוי' in detail and ('איזור' in detail or 'אזור' in detail) and 'גודל' not in detail and 'גובה' not in detail:
        return parse_area_designation_change(detail, lst_of_heb_words)
    if 'שימושים מותרים' in detail or ('קביעת' in detail and 'שימושים' in detail):
        return LandUseInstruction(detail)
    if 'עצים' in detail:
        return TreesInstruction(detail)
    if 'שימור' in detail:
        return PreservationInstruction(detail)
    if 'הריסה' in detail or 'הריסת' in detail or 'הריסות' in detail:
        return DestructionInstruction(detail)
    if 'היתר' in detail:
        return PermitInstruction(detail)
    if 'עיצוב אדריכלי' in detail:
        return ArchitecturalInstruction(detail)
    if 'שלבי' in detail:
        return StepInstruction(detail)
    if 'איחוד' in detail or 'חלוקה' in detail:
        return UnionAndDistributionInstruction(detail)
    if 'קווי בניין' in detail:
        return BuildingInstruction(detail)
    if 'שינוי' in detail and ('בניין' in detail or 'בנין' in detail):
        return BuildingInstruction(detail)
    if ('בנין' in detail or 'בניין' in detail) and 'קו' in detail:
        return BuildingInstruction(detail)
    if 'תכסית' in detail:
        return BuildingInstruction(detail)
    if 'זכויות בנייה' in detail or 'זכויות בניה' in detail:
        return BuildingInstruction(detail)
    if 'הגדלת' in detail or 'הקטנת' in detail or 'תוספת' in detail:
        return BuildingInstruction(detail)
    if 'הקמת' in detail:
        return BuildingInstruction(detail)
    if 'שימושים' in detail:  # this is not so sure
        return BuildingInstruction(detail)
    if 'בינוי' in detail:
        return BuildingInstruction(detail)
    if 'בנייה' in detail:
        return BuildingInstruction(detail)
    if 'קביעת' in detail:  # default for קביעת
        return BuildingInstruction(detail)
    return None


def parse_df(df, list_of_heb_words):
    instructions = [parse_detail(row['detail'], list_of_heb_words) for _, row in df.iterrows()]
    missing_value_prob = len([val for val in instructions if val is None]) / len(instructions)
    print('{} have no classification'.format(missing_value_prob))
    classifications_strings = [str(type(instruction)) for instruction in instructions]
    from_area = [instr.from_area if isinstance(instr, AreaDesignationChangeInstruction) else np.NaN for instr
                 in instructions]
    to_area = [instr.to_area if isinstance(instr, AreaDesignationChangeInstruction) else np.NaN for instr
               in instructions]
    return df.assign(classification=classifications_strings, from_area=from_area, to_area=to_area)


if __name__ == '__main__':
    df_heb_words = pd.read_excel('stopwords.xlsx')
    list_of_heb_words = [row['Undotted'] for _, row in df_heb_words.iterrows()]
    list_of_heb_words.remove('מדרך')   # it's a weird word and it's in there....
    list_of_heb_words.append('מתחם')
    parsed = parse_df(description_to_df(), list_of_heb_words)
    # parsed_filtered = parsed.drop(columns=['classification']).dropna(axis=0)
    parsed.to_excel('classifications.xlsx')
