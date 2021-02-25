import json
import re
import sys
import tracing

def check_date(key, ymin, ymax):
    def aux(value):
        try:
            value = int(value)
        except ValueError as err:
            tracing.warn("invalid '{key}': not a number {err}", key=key, err=err)
            return False

        return  ymin <= value <= ymax

    return aux


HGT_REGEX = r"^(?P<size>[0-9]+)(?P<unit>cm|in)$"

def valid_hgt(value):
    match = re.match(HGT_REGEX, value)

    if not match:
        tracing.warn("invalid 'hgt': '{val}' does not match '{rgx}'", val=value, rgx=HGT_REGEX)
        return False

    size = int(match.group("size"))
    unit = match.group("unit")

    if unit == "cm":
        return 150 <= size <= 193

    return 59 <= size <= 76

HCL_REGEX = r"^#[0-9a-f]{6}$"

def valid_hcl(value):
    match = re.match(HCL_REGEX, value)

    if not match:
        tracing.warn("invalid 'hcl': '{val}' does not match '{rgx}'", val=value, rgx=HCL_REGEX)
        return False

    return True

def valid_ecl(value):
    return value in ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]

PID_REGEX = r"^[0-9]{9}$"

def valid_pid(value):
    match = re.match(PID_REGEX, value)

    if not match:
        tracing.warn("invalid 'pid': '{val}' does not match '{rgx}'", val=value, rgx=PID_REGEX)
        return False

    return True

MANDATORIES = {
    "byr": check_date("byr", 1920, 2002),
    "iyr": check_date("iyr", 2010, 2020),
    "eyr": check_date("eyr", 2020, 2030),
    "hgt": valid_hgt,
    "hcl": valid_hcl,
    "ecl": valid_ecl,
    "pid": valid_pid,
}

def valid_passport(ppt, idx):
    tracing.info("passport: \n{ppt}", ppt=json.dumps(ppt, indent=4))

    for field, valid in MANDATORIES.items():
        if field not in ppt:
            tracing.warn("passport @{idx}: missing '{fld}'", idx=idx, fld=field)
            return False

        if not valid(ppt[field]):
            tracing.warn("passport @{idx}/{fld}: bad value '{val}'",
                         idx=idx, fld=field, val=ppt[field])
            return False

    tracing.info("passport @{idx}: ok'", idx=idx)
    return True


def main():
    count = 0
    passports = []

    passport = {}
    for _raw in sys.stdin:
        raw = _raw.strip()

        if raw == "":
            passports.append(passport)
            passport = {}
            continue

        for item in raw.split(" "):
            key, value = item.split(":")
            passport[key] = value

    passports.append(passport)


    for idx, passport in enumerate(passports):
        if valid_passport(passport, idx):
            count += 1

    tracing.info("found {count} valid passport{sfx}", count=count, sfx="s" if count > 1 else "")


if __name__ == "__main__":
    main()
