from app.models import Course
from app.models import Review
from datetime import datetime

class CourseRepository:
    def __init__(self, db):
        self.db = db

    def _all_query(self, name, category_ids):
        query = self.db.select(Course)

        if name:
            query = query.filter(Course.name.ilike(f'%{name}%'))

        if category_ids:
            query = query.filter(Course.category_id.in_(category_ids))

        return query

    def get_pagination_info(self, name=None, category_ids=None):
        query = self._all_query(name, category_ids)
        return self.db.paginate(query)

    def get_last_reviews(self, course_id, limit=5):
        return self.db.session.execute(
            self.db.select(Review)
            .filter_by(course_id=course_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
        ).scalars()

    def get_all_courses(self, name=None, category_ids=None, pagination=None):
        if pagination is not None:
            return pagination.items 
        
        return self.db.session.execute(self._all_query(name, category_ids)).scalars()

    def get_course_by_id(self, course_id):
        return self.db.session.get(Course, course_id)
    
    def new_course(self):
        return Course()

    def get_reviews(self, course_id, order='newest', page=1, per_page=5):
        from app.models import Review

        query = self.db.select(Review).filter_by(course_id=course_id)

        if order == 'positive':
            query = query.order_by(Review.rating.desc(), Review.created_at.desc())
        elif order == 'negative':
            query = query.order_by(Review.rating.asc(), Review.created_at.desc())
        else:  # newest
            query = query.order_by(Review.created_at.desc())

        return self.db.paginate(query, page=page, per_page=per_page)

    from app.models import Review

    def get_user_review(self, course_id, user_id):
        return self.db.session.execute(
            self.db.select(Review)
            .filter_by(course_id=course_id, user_id=user_id)
        ).scalar()

    def add_or_update_review(self, course_id, user_id, rating, text):
        review = self.get_user_review(course_id, user_id)

        if review:
            review.rating = rating
            review.text = text
            review.created_at = datetime.now()
        else:
            review = Review(course_id=course_id, user_id=user_id, rating=rating, text=text)
            self.db.session.add(review)

        self.db.session.flush()  # Обновление модели до пересчета рейтинга
        self.recalculate_rating(course_id)
        self.db.session.commit()

        return review

    def recalculate_rating(self, course_id):
        reviews = self.db.session.execute(
            self.db.select(Review).filter_by(course_id=course_id)
        ).scalars().all()

        rating_sum = sum(r.rating for r in reviews)
        rating_num = len(reviews)

        course = self.get_course_by_id(course_id)
        course.rating_sum = rating_sum
        course.rating_num = rating_num



    def add_course(self, author_id, name, category_id, short_desc, full_desc, background_image_id):
        course = Course(
            author_id=author_id,
            name=name,
            category_id=category_id,
            short_desc=short_desc,
            full_desc=full_desc,
            background_image_id=background_image_id
        )
        try:
            self.db.session.add(course)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e  # Пробрасываем любое другое исключение
        
        return course
