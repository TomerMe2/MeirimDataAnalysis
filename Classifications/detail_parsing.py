from dataclasses import dataclass
from Classifications.descriptions_to_data import description_to_df


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


def parse_detail(detail):
    if 'הפקעה' in detail:
        return ExpropriationInstruction(detail)
    if 'הנאה' in detail:
        return MovementInstruction(detail)
    if 'שינוי יעוד' in detail or 'שינוי ייעוד' in detail:
        return AreaDesignationChangeInstruction(detail)
    if 'עצים' in detail:
        return TreesInstruction(detail)
    if 'הריסה' in detail:
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
    if 'שינוי' in detail and 'בניין' in detail:
        return BuildingInstruction(detail)
    if 'תכסית' in detail:
        return BuildingInstruction(detail)
    if 'זכויות בנייה' in detail:
        return BuildingInstruction(detail)
    if 'שימושים' in detail:    # this is not so sure
        return BuildingInstruction(detail)
    if 'בינוי' in detail:
        return BuildingInstruction(detail)
    if 'בנייה' in detail:
        return BuildingInstruction(detail)
    if 'קביעת' in detail:     # default for קביעת
        return BuildingInstruction(detail)
    return None


def parse_df(df):
    instructions = [parse_detail(row['detail']) for _, row in df.iterrows()]
    missing_value_prob = len([val for val in instructions if val is None]) / len(instructions)
    print('{} have no classification'.format(missing_value_prob))
    classifications_strings = [str(type(instruction)) for instruction in instructions]
    return df.assign(classification=classifications_strings)


if __name__ == '__main__':
    parsed = parse_df(description_to_df())
    parsed.to_excel('classifications.xlsx')