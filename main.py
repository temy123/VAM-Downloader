from http.cookiejar import Cookie
from venv import create
import requests
import bs4
import os

page = 1

DOWNLOAD_PATH = "C:/Users/Hyunwoo Lee/VAM_Downloads/"

MAIN_HOST = "https://hub.virtamate.com"
MAIN_URL = f"{MAIN_HOST}/resources/categories/morphs.10/?page="

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
}

DEFAULT_COOKIES = {
    "vamhubconsent": "yes",
    "xf_user": "49952%2CJ9laP2hsJ9WoXmpdtYqAFqvEuD6tHhxSiq4YoNdS",
    "xf_csrf": "FVceIKHytkrnpSgx",
    "xf_session": "N5QisD58i38VHOP3KK1pPy143ex2hOek"
}


def get_html(url):
    response = requests.get(url, headers=DEFAULT_HEADERS,
                            cookies=DEFAULT_COOKIES)
    return response.text

# 페이지 리스트 접속


def get_page_list(page):
    html = get_html(f"{MAIN_URL}{page}")
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup

# Morph categories 접속 후 HTML 소스 가져오기


def get_morph_categories(soup):
    morph_categories = soup.find_all(class_="structItem-title")
    return morph_categories

# Detail 페이지에서 다운로드 링크 가져오기


def get_download_link(url):
    html = get_html(url)
    soup = bs4.BeautifulSoup(html, "html.parser")
    download_link = soup.find(class_="button--icon--download").get("href")
    download_link = f"{MAIN_HOST}{download_link}"
    return download_link

# 이미 있는 파일인지 확인


def is_file_exist(filename):
    return os.path.isfile(filename)

# 다운로드


def download_file(url, filename):
    response = requests.get(url, headers=DEFAULT_HEADERS,
                            cookies=DEFAULT_COOKIES)
    try:
        # 다운로드 경로에 파일 이름으로 저장
        with open(f"{DOWNLOAD_PATH}{filename}.var", "wb") as f:
            f.write(response.content)

        return True
    except Exception as e:
        return False


# 링크에서 다운로드 할 파일 이름 가져오기
def get_filename(url):
    return url.split("/")[-2]


# 다운로드 경로 생성
def create_download_path():
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)


# 수동으로 다운받아야 하는 파일들을 "list.txt" 파일에 append 하기
def append_to_list(link):
    with open(f"{DOWNLOAD_PATH}!!current_list.txt", "a") as f:
        f.write(link)


# '다음' 버튼이 있는 경우 true 반환하는 메소드
def has_next_page(soup):
    next_page = soup.find(class_="pageNavSimple-el--next")
    if next_page is None:
        return False
    else:
        return True


if __name__ == "__main__":
    create_download_path()

    while True:
        print(f"다운로드 시작 : {page} 페이지")
        soup = get_page_list(page)
        morph_categories = get_morph_categories(soup)
        for morph_category in morph_categories:
            # 2번째 a 태그에 있는 href 속성값 가져오기
            morph_category_url = morph_category.find_all("a")[1].get("href")
            morph_category_url = f"{MAIN_HOST}{morph_category_url}"

            # Detail 페이지에서 다운로드 링크 가져오기
            try:
                download_link = get_download_link(morph_category_url)
            except Exception as e:
                append_to_list(download_link)
                print(f"다운로드 링크 가져오기 실패 : {morph_category_url}")
                continue

            # 다운로드 링크에서 파일 이름 가져오기
            filename = get_filename(download_link)

            # 다운로드 경로에 파일이 있는지 확인
            if is_file_exist(f"{DOWNLOAD_PATH}{filename}.var"):
                print(f"{filename} : 이미 다운로드 되었습니다.")

            # 다운로드
            else:
                print(f"다운로드 시작 : {filename}")
                download_file(download_link, filename)
                print(f"다운로드 완료 : {filename}")

        print(f"다운로드 완료 : {page} 페이지")

        # 다음 페이지가 있는지 확인
        if has_next_page(soup):
            page += 1
        else:
            break
