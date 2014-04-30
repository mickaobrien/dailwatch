import csv
import os
import sys

def convert_pdf(pdf_file):
    """ Convert PDF file to txt file. """
    out_file = pdf_file.replace(".pdf", ".txt")
    os.system(("pdftotext %s %s") % (pdf_file, out_file))
    return out_file

def get_attendance(attendance_file, output_file):
    """ Parse attendance from txt file and write to output_file. """
    #with open("attendance.txt") as f:
    with open(attendance_file) as f:
        prev = None
        current_person = {}
        people = []
        for line in f:
            if "Deputy" in line and current_person == {}:
                current_person['name'] = get_name(prev)

            if "Sub-total" in line and 'name' in current_person.keys():
                number_days = int(line.split(": ")[1])
                current_person['days'] = number_days
                people.append(current_person)
                current_person = {}

            prev = line.strip()

        dicts_to_csv(people, output_file)

def get_name(line):
    """ Parse politician's name. """
    name_parts = line.split()
    if line[-1] == ".":
        #name has a middle initial
        middle_initial = name_parts[-1]
        first_name = name_parts[-2]
        surname = " ".join(name_parts[:-2])
        name = " ".join([first_name, middle_initial, surname])

    else:
        first_name = name_parts[-1]
        surname = " ".join(name_parts[:-1])
        name = " ".join([first_name, surname])

    return name

def dicts_to_csv(dicts, filename):
    """ Write a list of dicts to a csv file. """
    f = open(filename, 'wb')
    keys = dicts[0].keys()
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writer.writerow(keys)
    dict_writer.writerows(dicts)

if __name__ == "__main__":
    input_pdf = sys.argv[1]
    output_file = sys.argv[2]

    attendance_file = convert_pdf(input_pdf)
    get_attendance(attendance_file, output_file)

    # Clean up by removing intermediary txt file
    os.remove(attendance_file)
