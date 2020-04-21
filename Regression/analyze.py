from statsmodels.distributions.empirical_distribution import ECDF
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import data_tools
from Regression.plan_regressor import PlanRegressor as PlanRegressor
from Regression.plan import Plan as Plan


def draw_cat_unit(db, category, unit):
    vals = data_tools.get_conditional_vals(db, ['totalChange'], 'category = %s AND unit = %s', (category, unit),
                                           'plan_area_changes')
    vals = list(map(lambda tup: tup[0], vals))
    sns.set_style('whitegrid')
    ax = sns.kdeplot(np.array(vals))
    name = ' '.join([category, unit])
    ax.set_title(name[::-1])
    ax.set_xlabel(unit[::-1])
    ax.set_ylabel('density')
    plt.savefig('Graphs/{}'.format(name.replace('"', '').replace('/', '')))
    plt.show()


def draw_all_cats(db):
    crsr = db.cursor()
    crsr.execute("""SELECT category, unit
        FROM meirim.plan_area_changes
        GROUP BY category, unit""")
    tup_from_db = crsr.fetchall()
    cats_and_units = [data_tools.tup_to_readable_tup(tup) for tup in tup_from_db]
    [draw_cat_unit(db, tup[0], tup[1]) for tup in cats_and_units]

def draw_interesting_score(db):
    regressor = PlanRegressor(db, Plan.get_all_plans(db))
    scores = [plan_and_score[1] for plan_and_score in regressor.regress_all_plans()]
    sns.set_style('whitegrid')
    ax = sns.kdeplot(np.array(scores), bw=0.01)
    ax.set(xlim=(0, 1))  # scores are between 0 and 1
    ax.set_title('Plans Score According To Construction Size')
    ax.set_xlabel('score')
    ax.set_ylabel('density')
    plt.savefig('Graphs/ציון על בסיס שינויי בנייה')
    plt.show()


if __name__ == '__main__':
    db = data_tools.get_db()
    draw_all_cats(db)
    draw_interesting_score(db)