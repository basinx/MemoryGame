import csv

def load_questions(filename="questions.csv"):
    questions = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Exclude sections commented out with #
            # Expecting three columns: question, answer, extra info.
            if not row or row[0].startswith('#'):
                continue
            if len(row) == 3:
                questions.append((row[0], row[1], row[2]))
            elif len(row) == 2:
                questions.append((row[0], row[1], ""))
    return questions

