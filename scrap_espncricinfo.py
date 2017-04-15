import csv
import datetime
import requests
import random
from bs4 import BeautifulSoup

espn_url = 'http://www.espncricinfo.com'
stat_espn_url = 'http://stats.espncricinfo.com'
HEADERS = ['Team 1', 'Team 2', 'Winner',
           'Margin', 'Ground', 'Match Date', 'Year', 'Scorecard']


# grab content
def get_soup_for_url(url):
    """
    return a soup object for url
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    proxies = ["118.151.209.114", "124.124.1.178"]
    res = requests.get(url, headers=headers, proxies=random.choice(proxies))
    html_string = res.content
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup

# parse content


def get_menu_links(url):
    """
    from the given url, get yearwise links from submenu with menu name "Records"
    """
    soup = get_soup_for_url(url)
    links_div = soup.find('div', {'id': 'mag11'})
    links_table = links_div.find('table', {'id': 'mgDdRht'})
    links_tr = links_table.findAll('tr')
    ipl_links_yearwise_td = [tr.find('td') for tr in links_tr][1:]
    ipl_year_wise_links = []
    for each_year_td in ipl_links_yearwise_td:
        if each_year_td.a:
            ipl_year_wise_links.append(each_year_td.a['href'])
    return ipl_year_wise_links


def get_result_links(links):
    """
    from each year link get link of Match Result
    e.g: http://www.espncricinfo.com/indian-premier-league-2016/engine/series/968923.html?view=records
    """
    match_result_links = []
    for each_menu_link in links:
        ipl_page_link = espn_url + each_menu_link
        soup = get_soup_for_url(ipl_page_link)
        match_result_link = soup.findAll(string="Match results")[
            0].previous_element['href']
        match_result_links.append(stat_espn_url + match_result_link)
    return match_result_links


def get_match_data(urls):
    """
    extract match data match summary page
    e.g:http://stats.espncricinfo.com/indian-premier-league-2016/engine/records/team/match_results.html?id=11001;type=tournament
    """
    match_data = []
    for each_year_url in urls:
        soup = get_soup_for_url(each_year_url)
        table_div = soup.findAll('div', {'class': 'div630Pad'})
        content_tables = table_div[0].findAll('table')
        match_summary_table = content_tables[0]
        table_rows = match_summary_table.findAll('tr')
        headers = [
            each_header.text for each_header in match_summary_table.findAll('th')]
        table_body_content = match_summary_table.tbody.findAll('tr')
        for each_row in table_body_content:
            tds = each_row.findAll('td')
            row_data = [td.text for td in tds[0:-1]]
            if tds[-1].a:
                row_data.append(stat_espn_url + tds[-1].a['href'])
            else:
                row_data.append('NA')
            match_data.append(row_data)
    return match_data


# Store content
def write_to_csv(match_data):
    """
    store data collected in a CSV
    """
    with open('ipl_data.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(HEADERS)
        for row in match_data:
            row = [x.encode('utf-8') for x in row]
            try:
                match_date = datetime.datetime.strptime(row[5], '%b %d, %Y')
                row[5] = match_date.strftime('%m-%d-%Y')
                row.insert(6, match_date.strftime('%Y'))
            except:
                row[5] = 'NA'
                row.insert(6, 'NA')
            print row
            csvwriter.writerow(row)


def main():
    master_url = 'http://www.espncricinfo.com/indian-premier-league-2017/engine/series/1078425.html?view=records'
    ipl_menu_links = get_menu_links(master_url)
    match_result_links = get_result_links(ipl_menu_links)
    match_data = get_match_data(match_result_links)
    write_to_csv(match_data)

if __name__ == "__main__":
    main()
