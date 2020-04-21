from shapely import wkt

import data_tools


class AreaChange:

    def __init__(self, tup_from_changes_tbl):
        tup = data_tools.tup_to_readable_tup(tup_from_changes_tbl)
        self.id = tup[0]
        self.category = tup[1]
        self.unit = tup[2]
        self.approved_state = tup[3]
        self.change_to_approved_state = tup[4]
        self.total_change = tup[5]


class Plan:
    TABLE_NAME = 'plan'
    PLAN_AREA_CHANGES_TBL_NM = 'plan_area_changes'

    def __init__(self, db, tup_from_plans_tbl):
        tup = data_tools.tup_to_readable_tup(tup_from_plans_tbl)
        self.id = tup[0]
        self.sent = tup[1]
        self.object_id = tup[2]
        self.county = tup[3]
        self.pl_number = tup[4]
        self.url = tup[5]
        self.jurisdiction = tup[6]
        self.status = tup[7]
        self.polygon = wkt.loads(tup[8])
        plan_area_changes_clms = ['changeId', 'category', 'unit', 'approvedState',
                                  'changeToApprovedState', 'totalChange']
        tups_from_db = data_tools.get_conditional_vals(db, plan_area_changes_clms, 'planId = %s', (self.id,),
                                                       Plan.PLAN_AREA_CHANGES_TBL_NM)
        self.area_changes = [AreaChange(tp) for tp in tups_from_db]

    @staticmethod
    def get_all_plans(db):
        interesting_clms = ['id', 'sent', 'OBJECTID', 'PLAN_COUNTY_NAME', 'PL_NUMBER', 'plan_url',
                            'jurisdiction', 'status', 'ST_AsText(geom)']
        ans_from_db = data_tools.get_vals(db, interesting_clms, Plan.TABLE_NAME)
        return [Plan(db, tup) for tup in ans_from_db]
