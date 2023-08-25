def get_paginated_response(paginator, data):
    return {'total_pages': paginator.page.paginator.num_pages,
            'current_page': paginator.page.number,
            'total_data_count': paginator.page.paginator.count,
            'data': data
            }
