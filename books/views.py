from django.shortcuts import render, get_object_or_404
from .models import Category, Book
from .external_api import search_books, get_book_details, get_book_recommendations, get_popular_books

def book_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    
    # Google Books API를 통해 책을 가져옵니다
    all_books = []
    
    # 기본 쿼리로 책을 가져옴 (알파벳 순)
    alphabet_query = 'intitle:a OR intitle:b OR intitle:c OR intitle:d'
    books_data = search_books(alphabet_query, max_results=30)
    
    if books_data and 'items' in books_data:
        for item in books_data['items']:
            book_info = item.get('volumeInfo', {})
            all_books.append({
                'id': item.get('id', ''),
                'title': book_info.get('title', '제목 없음'),
                'authors': book_info.get('authors', ['작가 미상']),
                'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'published_date': book_info.get('publishedDate', ''),
                'rating': book_info.get('averageRating', 0)
            })
    
    # 알파벳 순으로 정렬
    all_books.sort(key=lambda x: x['title'].lower())
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # 카테고리에 맞는 책만 필터링 (실제로는 API 호출 필요)
        category_books = get_book_recommendations(category.name, max_results=15)
        filtered_books = []
        
        if category_books and 'items' in category_books:
            for item in category_books['items']:
                book_info = item.get('volumeInfo', {})
                filtered_books.append({
                    'id': item.get('id', ''),
                    'title': book_info.get('title', '제목 없음'),
                    'authors': book_info.get('authors', ['작가 미상']),
                    'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                    'published_date': book_info.get('publishedDate', ''),
                    'rating': book_info.get('averageRating', 0)
                })
            
            # 알파벳 순으로 정렬
            filtered_books.sort(key=lambda x: x['title'].lower())
            all_books = filtered_books
    
    return render(request, 
                  'books/book_list.html', 
                  {'category': category,
                   'categories': categories,
                   'books': all_books,
                   'is_api_data': True})  # API 데이터임을 템플릿에 알려줌

def book_detail(request, id, slug):
    book = get_object_or_404(Book, id=id, slug=slug)
    
    # 관련 책 추천 기능 (책 카테고리 기반)
    related_books_data = get_book_recommendations(book.category.name, max_results=4)
    related_books = []
    
    if related_books_data and 'items' in related_books_data:
        for item in related_books_data['items']:
            book_info = item.get('volumeInfo', {})
            # 우리 DB에 있는 책을 피하기 위한 확인 로직 추가 필요
            book_title = book_info.get('title', '제목 없음')
            if book_title != book.title:  # 현재 보고 있는 책은 제외
                related_books.append({
                    'id': item.get('id', ''),
                    'title': book_title,
                    'authors': book_info.get('authors', ['작가 미상']),
                    'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                    'categories': book_info.get('categories', ['일반']),
                    'rating': book_info.get('averageRating', 0)
                })
    
    return render(request,
                  'books/book_detail.html',
                  {'book': book,
                   'related_books': related_books[:4]})  # 최대 4개까지만 표시

def category_list(request):
    # 전체 베스트셀러
    bestsellers_data = get_popular_books(max_results=20)
    bestseller_books = []
    
    if bestsellers_data and 'items' in bestsellers_data:
        for item in bestsellers_data['items']:
            # items가 직접 책 객체인 경우
            if isinstance(item, dict) and 'id' in item:
                bestseller_books.append(item)
            # 원래 API 구조대로 volumeInfo가 있는 경우
            elif isinstance(item, dict) and 'volumeInfo' in item:
                book_info = item.get('volumeInfo', {})
                bestseller_books.append({
                    'id': item.get('id', ''),
                    'title': book_info.get('title', '제목 없음'),
                    'authors': book_info.get('authors', ['작가 미상']),
                    'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                    'rating': book_info.get('averageRating', 0)
                })
    
    # 분야별 베스트셀러
    category_bestsellers = []
    categories = ['fiction', 'history', 'business', 'science', 'technology']
    
    for category in categories:
        # 쿼리를 명확히 하고 쿼리 형식 수정
        category_data = get_book_recommendations(f'subject:{category}', max_results=4)
        category_books = []
        
        if category_data and 'items' in category_data:
            for item in category_data['items']:
                book_info = item.get('volumeInfo', {})
                category_books.append({
                    'id': item.get('id', ''),
                    'title': book_info.get('title', '제목 없음'),
                    'authors': book_info.get('authors', ['작가 미상']),
                    'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                    'rating': book_info.get('averageRating', 0)
                })
        
        # 결과가 있는 경우에만 카테고리를 추가 (빈 리스트 확인 수정)
        if len(category_books) > 0:
            category_bestsellers.append({
                'name': category.capitalize(),
                'books': category_books
            })
    
    # 디버깅용 코드 추가
    print(f"카테고리 베스트셀러 수: {len(category_bestsellers)}")
    for cat in category_bestsellers:
        print(f"{cat['name']}: {len(cat['books'])} 권의 책")
    
    return render(request, 'books/category_list.html', {
        'bestsellers': bestseller_books,
        'category_bestsellers': category_bestsellers
    })

def search_results(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        data = search_books(query)
        if data and 'items' in data:
            for item in data['items']:
                book_info = item.get('volumeInfo', {})
                results.append({
                    'id': item.get('id', ''),
                    'title': book_info.get('title', '제목 없음'),
                    'authors': book_info.get('authors', ['작가 미상']),
                    'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                    'categories': book_info.get('categories', ['일반']),
                    'description': book_info.get('description', '설명 없음')[:200] + '...',
                    'rating': book_info.get('averageRating', 0)
                })
    
    return render(request, 'books/search_results.html', {'query': query, 'results': results})

def api_book_detail(request, book_id):
    book_data = get_book_details(book_id)
    book = None
    related_books = []
    
    if book_data:
        book_info = book_data.get('volumeInfo', {})
        book = {
            'id': book_data.get('id', ''),
            'title': book_info.get('title', '제목 없음'),
            'subtitle': book_info.get('subtitle', ''),
            'authors': book_info.get('authors', ['작가 미상']),
            'publisher': book_info.get('publisher', '출판사 미상'),
            'published_date': book_info.get('publishedDate', ''),
            'description': book_info.get('description', '설명 없음'),
            'page_count': book_info.get('pageCount', 0),
            'categories': book_info.get('categories', ['일반']),
            'rating': book_info.get('averageRating', 0),
            'ratings_count': book_info.get('ratingsCount', 0),
            'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
            'language': book_info.get('language', '')
        }
        
        # 관련 책 추천 (같은 카테고리)
        if 'categories' in book_info and book_info['categories']:
            category = book_info['categories'][0]
            rec_data = get_book_recommendations(category, max_results=4)
            if rec_data and 'items' in rec_data:
                for item in rec_data['items']:
                    item_info = item.get('volumeInfo', {})
                    if item.get('id') != book_id:  # 현재 책은 제외
                        related_books.append({
                            'id': item.get('id', ''),
                            'title': item_info.get('title', '제목 없음'),
                            'authors': item_info.get('authors', ['작가 미상']),
                            'thumbnail': item_info.get('imageLinks', {}).get('thumbnail', ''),
                        })
    
    return render(request, 'books/api_book_detail.html', {'book': book, 'related_books': related_books[:4]})

def recommendations(request):
    # 사용자 관심사 기반 추천 (여기서는 간단히 카테고리로 처리)
    interest = request.GET.get('interest', 'fiction')  # 기본값은 fiction
    recommended_books = []
    
    data = get_book_recommendations(interest, max_results=8)
    if data and 'items' in data:
        for item in data['items']:
            book_info = item.get('volumeInfo', {})
            recommended_books.append({
                'id': item.get('id', ''),
                'title': book_info.get('title', '제목 없음'),
                'authors': book_info.get('authors', ['작가 미상']),
                'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'categories': book_info.get('categories', ['일반']),
                'rating': book_info.get('averageRating', 0)
            })
    
    # 인기 책 목록
    popular_books = []
    pop_data = get_popular_books(max_results=4)
    if pop_data and 'items' in pop_data:
        for item in pop_data['items']:
            book_info = item.get('volumeInfo', {})
            popular_books.append({
                'id': item.get('id', ''),
                'title': book_info.get('title', '제목 없음'),
                'authors': book_info.get('authors', ['작가 미상']),
                'thumbnail': book_info.get('imageLinks', {}).get('thumbnail', ''),
                'rating': book_info.get('averageRating', 0)
            })
    
    # 카테고리 목록 (관심사 선택용)
    interests = ['fiction', 'science', 'history', 'biography', 'business', 'technology', 'self-help', 'cooking']
    
    return render(request, 'books/recommendations.html', {
        'recommended_books': recommended_books,
        'popular_books': popular_books,
        'interests': interests,
        'selected_interest': interest
    })