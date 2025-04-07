import requests
from django.conf import settings

def search_books(query, max_results=10):
    """
    Google Books API를 사용하여 책을 검색합니다.
    """
    endpoint = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': query,
        'maxResults': max_results,
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_book_details(book_id):
    """
    Google Books API를 사용하여 특정 책의 상세 정보를 가져옵니다.
    """
    endpoint = f'https://www.googleapis.com/books/v1/volumes/{book_id}'
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    return None

def get_book_recommendations(category, max_results=10):
    """
    특정 카테고리나 키워드에 기반하여 책을 추천합니다.
    """
    endpoint = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': f'subject:{category}',
        'maxResults': max_results,
        'orderBy': 'relevance'
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_popular_books(max_results=20):
    """
    인기 있는 책들을 가져옵니다.
    여러 쿼리와 매개변수를 사용하여 다양한 인기 책을 수집합니다.
    """
    all_books = []
    book_ids = set()  # 중복 방지를 위한 ID 집합
    
    # 다양한 쿼리 사용
    queries = [
        'subject:bestseller',
        'subject:popular',
        'subject:award',
        'subject:fiction bestseller',
        'subject:nonfiction bestseller'
    ]
    
    # 여러 정렬 방식 사용
    ordering = ['relevance', 'newest']
    
    endpoint = 'https://www.googleapis.com/books/v1/volumes'
    
    # 각 쿼리와 정렬 방식 조합으로 책 검색
    for query in queries:
        for order in ordering:
            params = {
                'q': query,
                'maxResults': 10,  # 각 쿼리당 10개까지만 가져옴
                'orderBy': order
            }
            
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data:
                    for item in data['items']:
                        book_id = item.get('id')
                        if book_id and book_id not in book_ids:  # 중복 방지
                            book_ids.add(book_id)
                            book_info = item.get('volumeInfo', {})
                            all_books.append({
                                'id': book_id,
                                'title': book_info.get('title', '제목 없음'),
                                'authors': book_info.get('authors', ['작가 미상']),
                                'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                                'rating': book_info.get('averageRating', 0)
                            })
                            
                            # 지정된 최대 결과 수에 도달하면 중단
                            if len(all_books) >= max_results:
                                return {'items': all_books}
    
    # 결과를 Google Books API 응답 형식으로 반환
    return {'items': all_books} if all_books else None