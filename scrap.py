import csv
import time
import requests
from bs4 import BeautifulSoup


"""
Extract text and code from a div element
"""
def extract_text_with_code(question_div):
    result_text = ""
    p_tags = question_div.find_all('p')
    code_tags = question_div.find_all('pre')
    for i in range(max(len(p_tags), len(code_tags))):
        if i < len(p_tags):
            result_text += p_tags[i].get_text() + "\n"
        if i < len(code_tags):
            code_text = code_tags[i].find('code').get_text() if code_tags[i].find('code') else ""
            result_text += f"<code>{code_text}</code>\n"
    return result_text.replace('\n', ' ')


"""
Scrap data from stackoverflow, only keep posts with accepted answer
Return question_title, question_text, answer_text
"""
def get_stackoverflow_data(question_id):
    url = f"https://stackoverflow.com/questions/{question_id}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        not_found_heading = soup.find('h1', text="Page not found")
        if not_found_heading:
            print(f"{question_id} not found")
            return None, None, None
        # Check if there is an accepted answer div
        accepted_answer_div = soup.find('div', class_='accepted-answer')
        if accepted_answer_div:
            # question parsing
            question_div = soup.find('div', class_='postcell')
            question_body = question_div.find('div', class_='js-post-body')
            question_text = extract_text_with_code(question_body)
            question_title = soup.title.string
            # answer parsing
            answer_text = extract_text_with_code(accepted_answer_div.find('div', class_='js-post-body'))
            return question_title, question_text, answer_text
    else:
        print(f"{question_id}-> {response.status_code}")
        return None, None, None


def save_to_csv(filename, data):
    with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data)


if __name__ == "__main__":
    csv_filename = "accepted_answers.csv"
    for question_id in range(2932, 2933):
        result = get_stackoverflow_data(question_id)
        if (result is not None) and (result[0] is not None) and (result[0] != ""):
            title, question, answer = result
            save_to_csv(csv_filename, [question_id, title, question, answer])
            print(f"Question ID {question_id}: Saved to CSV")
        else:
            print(f"Question ID {question_id}: not saved")
        time.sleep(1)
