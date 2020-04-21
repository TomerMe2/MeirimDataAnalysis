import json
import statistics

import data_tools
from data_tools import get_vals
from Regression.plan import Plan
from Regression.plan_regressor import PlanRegressor


def table_jibrish_to_data(jibrish):
    if jibrish is None:
        return []
    jibrish_json = json.loads(jibrish)[0]
    return [{'category': single_jibrish['3'][:single_jibrish['3'].find(' (')],
             'unit': single_jibrish['4'],
             'approved_state': '0' if single_jibrish['5'] is None or single_jibrish['5'] is '' else
             single_jibrish['5'].replace(',', ''),
             'change_to_approved_state': '0' if single_jibrish['6'] is None or single_jibrish['6'] is '' else
             single_jibrish['6'].replace(',', ''),
             'total_change': '0' if single_jibrish['7'] is None or single_jibrish['7'] is '' else
             single_jibrish['7'].replace(',', '')}
            for single_jibrish in jibrish_json]


def fill_meta_new_tbl(db):
    plan_tbl = get_vals(db, ['id', 'areaChanges'])
    create_tbl_query = """CREATE TABLE plan_area_changes(
        changeId int NOT NULL AUTO_INCREMENT,
        planId int,
        category varchar(255),
        unit varchar(255),
        approvedState double,
        changeToApprovedState double,
        totalChange double,
        PRIMARY KEY (changeId),
        FOREIGN KEY (planId) REFERENCES meirim.plan(id))"""
    for row_in_plan in plan_tbl:
        for data_dict in table_jibrish_to_data(row_in_plan[1]):
            db.cursor().execute("""INSERT INTO meirim.plan_area_changes (planId, category, unit, approvedState, 
            changeToApprovedState, totalChange) VALUES (%s, %s, %s, %s, %s, %s)""",
                                (row_in_plan[0],
                                 data_dict['category'], data_dict['unit'], float(data_dict['approved_state']),
                                 float(data_dict['change_to_approved_state']), float(data_dict['total_change'])))
    db.commit()


def check_what_changes_can_be(db):
    clmn = ['areaChanges']
    vals = get_vals(db, clmn)
    print(vals)
    cntr = {}
    for row in vals:
        data = table_jibrish_to_data(row[0])
        for row_in_json_tbl in data:
            item = row_in_json_tbl['category']
            if item not in cntr:
                cntr[item] = 0
            cntr[item] += 1
    return cntr


def total_all_categories_statistics(self, db):
    """
    BAD FUNCTION. SHOULD BE DONE IN SQL
    """
    def get_plan_area_changes(plan_id):
        interesting_clms = ['category', 'unit', 'approvedState', 'changeToApprovedState', 'totalChange']
        return list(map(data_tools.tup_to_readable_tup,
                        data_tools.get_conditional_vals(db, interesting_clms, 'planId = %s', params=(plan_id,),
                                                        table='plan_area_changes')))

    plans = data_tools.get_vals(db, data_tools.INTERESTING_CLMNS)
    dict = {}
    for pln in plans:
        changes = get_plan_area_changes(pln[0])
        for change in changes:
            cat = ' '.join([change[0], change[1]])
            if cat not in dict:
                dict[cat] = []
            dict[cat].append(change[-1])
    str_to_write = ''
    for key, value in dict.items():
        str_to_write += key + '- ' + 'mean: ' + str(statistics.mean(value)) + ' stdev: ' + \
                        str(statistics.stdev(value)) + '\n'
    file = open('total_all_categories_statistics.txt', 'w')
    file.write(str_to_write)
    file.close()

def check_regressor():
    def print_regressed_element(ele):
        print(str(ele[0].id) + ' score: ' + str(ele[1]))

    db = data_tools.get_db()
    plans = Plan.get_all_plans(db)
    regressor = PlanRegressor(db)
    regressed = [(pln, regressor.regress(pln)) for pln in plans]
    ordered = sorted(regressed, key=lambda tup: tup[1])  # sort from lower to higher
    top_interesting = 5
    print('interesting: ' + str(top_interesting))
    for i in range(1, top_interesting + 1):
        print_regressed_element(ordered[-i])
    top_not_interesting = 5
    print('not interesting: ' + str(top_not_interesting))
    for i in range(0, top_not_interesting):
        print_regressed_element(ordered[i])


if __name__ == '__main__':
    db = data_tools.get_db()
    #sql = 'SELECT ST_AsText(geom) AS geom FROM meirim.plan LIMIT 1'
    #cursor = db.cursor()
    #cursor.execute(sql)
    #dt = cursor.fetchall()[0][0]
    #wkt_dt = wkt.loads(dt)
    #center = wkt_dt.centroid
    all_plans = Plan.get_all_plans(db)
    regressor = PlanRegressor(db, all_plans)
    regressed = regressor.regress_all_plans()
    deb = True