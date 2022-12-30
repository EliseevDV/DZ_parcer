
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
import csv

def get_vacancy_info(soup, link):
    description = soup.find_all('p')
    for paragraph in description:
        if "Django" in paragraph.text or "Flask" in paragraph.text:
            vacancy = {
                'link': link,
                'name': soup.find('h1', class_='bloko-header-section-1').text,
                'employer_name': soup.find('a', class_='bloko-link bloko-link_kind-tertiary').text,
                'salary_from': soup.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text,
                'city': '',
                }
            city_attributes = ['vacancy-view-raw-address', 'vacancy-view-location']
            city = None
            for attribute in city_attributes:
                city = soup.find(attrs={'data-qa': attribute})
                if city:
                    break
            if city:
                vacancy['city'] = city.text
            # print(vacancy)
            return vacancy

def parse_vacancy(link):
    headers = Headers(browser='fierfox', os='win').generate()
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    vacancy = get_vacancy_info(soup, link)
    return vacancy

def parse_vacancies():
    page_for_parsing = int(input('Введите количество страниц для обработки:  '))
    search_url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    params = {
    'L_is_autosearch': 'false',
    # 'area': '1,2',
    'clusters': 'true',
    'enable_snippets': 'true',
    # 'text': 'Python',
    'specialization': '1.221',
    'page': 0
    }
    vacancies = []
    while True:

        if params['page'] > page_for_parsing:
            break
        headers = Headers(browser='fierfox', os='win').generate()
        response = requests.get(search_url, params=params, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        vacancy_blocks = soup.find_all('div', class_='serp-item')
        for block in vacancy_blocks:
            link = block.find('a').get('href')
            vacancy = parse_vacancy(link)
            if vacancy is not None:
                vacancies.append(vacancy)

        print(f"[INFO] Обработана страница {params['page']}")
        params['page'] += 1

        with open('vacancies.json', 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=4)
        with open('data_HH.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, ['link', 'name', 'employer_name', 'salary_from', 'city'])
            writer.writeheader()
            writer.writerows(vacancies)

def main():
    parse_vacancies()


if __name__ == "__main__":
    main()


