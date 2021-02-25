import json
import sys
import tracing

PASSPORTS = []
MANDATORIES = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]

def main():
    count = 0

    passport = {}
    for _raw in sys.stdin:
        raw = _raw.strip()

        if raw == "":
            PASSPORTS.append(passport)
            passport = {}
            continue

        for item in raw.split(" "):
            key, value = item.split(":")
            passport[key] = value

    PASSPORTS.append(passport)

    pass_str = json.dumps(PASSPORTS, indent=4)
    tracing.info("passports: \n{pass_str}", pass_str=pass_str)

    for idx, passport in enumerate(PASSPORTS):
        for field in MANDATORIES:
            if field not in passport:
                tracing.info("passport @{idx} is invalid: missing '{field}'", idx=idx, field=field)
                count +=1
                break

    tracing.info("found {count} invalid passport{sfx}", count=count, sfx="s" if count > 1 else "")

    count = len(PASSPORTS) - count
    tracing.info("found {count} valid passport{sfx}", count=count, sfx="s" if count > 1 else "")


if __name__ == "__main__":
    main()
