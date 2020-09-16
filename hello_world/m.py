"""Mapping classes for our ORM."""
from sqlalchemy import Table, Column, Integer, Numeric, String, Boolean, Sequence, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

Base = declarative_base()


# Relational tables.


def init(table_schema='per_school'):
    global area_tag
    area_tag = Table('area_tag', Base.metadata,
        Column('area_id', Integer, ForeignKey('{}.area.id'.format(table_schema))),
        Column('tag_id', Integer, ForeignKey('{}.tag.id'.format(table_schema))),
        Column('weight', Integer),

        schema = table_schema
    )

    global area_feature
    area_feature = Table('area_feature', Base.metadata,
        Column('area_id', Integer, ForeignKey('{}.area.id'.format(table_schema))),
        Column('feature_id', Integer, ForeignKey('{}.feature.id'.format(table_schema))),
        Column('weight', Integer),

        schema = table_schema
    )

    global feature_section
    feature_section = Table('feature_section', Base.metadata,
        Column('feature_id', Integer, ForeignKey('{}.feature.id'.format(table_schema))),
        Column('section_id', Integer, ForeignKey('{}.section.id'.format(table_schema))),

        schema = table_schema
    )

    global feature_image
    feature_image = Table('feature_image', Base.metadata,
        Column('feature_id', Integer, ForeignKey('{}.feature.id'.format(table_schema))),
        Column('image_id', Integer, ForeignKey('{}.image.id'.format(table_schema))),

        schema = table_schema
    )

    global feature_video
    feature_video = Table('feature_video', Base.metadata,
        Column('feature_id', Integer, ForeignKey('{}.feature.id'.format(table_schema))),
        Column('video_id', Integer, ForeignKey('{}.video.id'.format(table_schema))),

        schema = table_schema
    )

    global FeatureTour
    class FeatureTour(Base):
        __tablename__ = 'feature_tour'
        feature_id = Column(Integer, ForeignKey('{}.feature.id'.format(table_schema)), primary_key=True)
        tour_id = Column(Integer, ForeignKey('{}.tour.id'.format(table_schema)), primary_key=True)

        area_ids = Column(String)
        
        feature = relationship('Feature', back_populates='_feature_tours')
        tour = relationship('Tour', back_populates='_feature_tours')

        __table_args__ = {'schema': table_schema}


    # Mappings.


    global Feature
    class Feature(Base):
        __tablename__ = 'feature'
        __plural__ = 'features'

        id = Column(Integer, Sequence('feature_id_seq', schema=table_schema), primary_key=True)

        latitude = Column(Numeric, nullable=False)
        longitude = Column(Numeric, nullable=False)
        altitude = Column(Numeric, nullable=False)

        title = Column(String, nullable=False)
        tldr = Column(String, nullable=False)

        # Standard relationships.
        areas = relationship('Area', secondary=area_feature, back_populates='features')
        sections = relationship('Section', secondary=feature_section, back_populates='features')
        images = relationship('Image', secondary=feature_image, back_populates='features')
        videos = relationship('Video', secondary=feature_video, back_populates='features')

        _feature_tours = relationship('FeatureTour', back_populates='feature')

        # Proxy relationships.
        # Features are related to tours directly. We just use an intermediate table so we need a proxy for QoL.
        tours = association_proxy('_feature_tours', 'tour')
        # Tags is found by a double join feature->area->tag.
        tags = association_proxy('areas', 'tags')
    
        enterable = Column(Boolean, nullable=False)
        tourable = Column(Boolean, nullable=False)

        __table_args__ = {'schema': table_schema}

    global Tag
    class Tag(Base):
        __tablename__ = 'tag'
        __plural__ = 'tags'

        id = Column(Integer, Sequence('tag_id_seq', schema=table_schema), primary_key=True)

        category_id = Column(Integer, ForeignKey('{}.category.id'.format(table_schema)), nullable=False)
        question_id = Column(Integer, ForeignKey('{}.question.id'.format(table_schema)), nullable=False)

        category = relationship('Category', back_populates='tags')
        question = relationship('Question', back_populates='tags')
        areas = relationship('Area', secondary=area_tag, back_populates='tags')

        title = Column(String, nullable=False)

        __table_args__ = {'schema': table_schema}
        
    global Category
    class Category(Base):
        __tablename__ = 'category'
        __plural__ = 'categories'

        id = Column(Integer, Sequence('category_id_seq', schema=table_schema), primary_key=True)

        title = Column(String, nullable=False)

        tags = relationship('Tag', back_populates='category')

        __table_args__ = {'schema': table_schema}
        
    global Tour
    class Tour(Base):
        __tablename__ = 'tour'
        __plural__ = 'tours'

        id = Column(Integer, Sequence('tour_id_seq', schema=table_schema), primary_key=True)

        index = Column(Integer, nullable=False, unique=True)

        title = Column(String, nullable=False)
        tldr = Column(String, nullable=False)

        _feature_tours = relationship('FeatureTour', back_populates='tour')
        features = association_proxy('_feature_tours', 'feature')
        #area_ids = association_proxy('_feature_tours', 'area_ids')

        __table_args__ = {'schema': table_schema}
        
    global Question
    class Question(Base):
        __tablename__ = 'question'
        __plural__ = 'questions'

        id = Column(Integer, Sequence('question_id_seq', schema=table_schema), primary_key=True)

        index = Column(Integer, nullable=False, unique=True)

        title = Column(String, nullable=False)
        subtitle = Column(String, nullable=False)

        categorized = Column(Boolean, nullable=False)
        multi = Column(Boolean, nullable=False)

        tags = relationship('Tag', back_populates='question')

        __table_args__ = {'schema': table_schema}
        
    global Area
    class Area(Base):
        __tablename__ = 'area'
        __plural__ = 'areas'

        id = Column(Integer, Sequence('area_id_seq', schema=table_schema), primary_key=True)

        title = Column(String, nullable=False)
        tldr = Column(String, nullable=False)

        sections = relationship('Section', back_populates='area')
        features = relationship('Feature', secondary=area_feature, back_populates='areas')
        tags = relationship('Tag', secondary=area_tag, back_populates='areas')

        alone = Column(Boolean, nullable=False)

        __table_args__ = {'schema': table_schema}

    global Section
    class Section(Base):
        __tablename__ = 'section'
        __plural__ = 'sections'

        id = Column(Integer, Sequence('section_id_seq', schema=table_schema), primary_key=True)

        area_id = Column(Integer, ForeignKey('{}.area.id'.format(table_schema)), nullable=False)

        title = Column(String, nullable=False)
        body = Column(String, nullable=False)

        area = relationship('Area', back_populates='sections')
        features = relationship('Feature', secondary=feature_section, back_populates='sections')

        show = Column(Boolean, nullable=False)

        __table_args__ = {'schema': table_schema}
        
    global Image
    class Image(Base):
        __tablename__ = 'image'
        __plural__ = 'images'

        id = Column(Integer, Sequence('image_id_seq', schema=table_schema), primary_key=True)

        title = Column(String, nullable=False)
        url = Column(String, nullable=False)

        features = relationship('Feature', secondary=feature_image, back_populates='images')

        __table_args__ = {'schema': table_schema}

    global Video
    class Video(Base):
        __tablename__ = 'video'
        __plural__ = 'video'

        id = Column(Integer, Sequence('video_id_seq', schema=table_schema), primary_key=True)

        title = Column(String, nullable=False)
        url = Column(String, nullable=False)

        features = relationship('Feature', secondary=feature_video, back_populates='videos')

        __table_args__ = {'schema': table_schema}

    global AVAILABLE_RESOURCES
    AVAILABLE_RESOURCES = [Feature, Tag, Tour, Category, Question]

class School(Base):
    __tablename__ = 'school'
    __plural__ = 'schools'

    sid = Column(String, primary_key=True)

    title = Column(String, nullable=False)
    primary_color = Column(String, nullable=False)

    __table_args__ = {'schema': 'meta'}
