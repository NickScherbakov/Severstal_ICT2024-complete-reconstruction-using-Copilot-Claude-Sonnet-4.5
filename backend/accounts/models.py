import io

from django.core.files.base import ContentFile
from django.db import models
from export import preprocess_blocks, save_pdf_report, save_excel_report, save_word_report

class Site(models.Model):
    domain = models.CharField(
        'Домен'
    )

    class Meta:
        verbose_name = 'Проверенный сайт'
        verbose_name_plural = 'Проверенные сайты'

    def __str__(self) -> str:
        return self.domain


class SearchQuery(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='search_queries',
        verbose_name='Пользователь',
        null=True
    )
    text = models.TextField(
        'Текст запроса пользователя',
        max_length=400
    )
    updates_subscribe = models.BooleanField(
        'Подписка на обновления',
        default=False
    )
    data = models.ManyToManyField(
        'Data',
        verbose_name='Данные',
        related_name='search_queries'
    )

    class Meta:
        verbose_name = 'Поисковый запрос'
        verbose_name_plural = 'Поисковые запросы'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'text'],
                name='%(app_label)s_%(class)s_uniq'
            )
        ]

    def __str__(self) -> str:
        return f'{self.text}'


class Theme(models.Model):
    name = models.CharField(
        'Название'
    )

    class Meta:
        verbose_name = 'Тематика отчета'
        verbose_name_plural = 'Тематики отчетов'

    def __str__(self) -> str:
        return self.name


class Template(models.Model):
    name = models.CharField(
        'Название'
    )
    theme = models.ForeignKey(
        'Theme',
        on_delete=models.SET_NULL,
        related_name='templates',
        verbose_name='Тематика отчета',
        null=True
    )
    category = models.ForeignKey(
        'TemplateCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates',
        verbose_name='Категория'
    )
    description = models.TextField(
        'Описание',
        blank=True
    )
    is_public = models.BooleanField(
        'Публичный',
        default=False
    )
    is_premium = models.BooleanField(
        'Премиум',
        default=False
    )
    tags = models.JSONField(
        'Теги',
        default=list,
        blank=True
    )
    use_count = models.IntegerField(
        'Количество использований',
        default=0
    )
    rating = models.FloatField(
        'Рейтинг',
        default=0.0
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Шаблон отчета'
        verbose_name_plural = 'Шаблоны отчетов'

    def __str__(self) -> str:
        return self.name


class MetaBlock(models.Model):
    PLOTLY = 'plotly'
    TEXT = 'text'
    VIDEO = 'video'
    TABLE = 'table'
    MAP = 'map'
    TIMELINE = 'timeline'
    NETWORK = 'network'
    COMPARISON = 'comparison'
    SENTIMENT = 'sentiment'
    FORECAST = 'forecast'
    # New enterprise processors
    ANOMALY = 'anomaly'
    RECOMMENDATION = 'recommendation'
    TREND = 'trend'
    CLUSTERING = 'clustering'
    SUMMARY = 'summary'
    
    TYPES = (
        (PLOTLY, 'Plotly'),
        (TEXT, 'Текст'),
        (VIDEO, 'Видео'),
        (TABLE, 'Таблица'),
        (MAP, 'Карта'),
        (TIMELINE, 'Таймлайн'),
        (NETWORK, 'Граф связей'),
        (COMPARISON, 'Сравнение'),
        (SENTIMENT, 'Анализ тональности'),
        (FORECAST, 'Прогноз'),
        (ANOMALY, 'Обнаружение аномалий'),
        (RECOMMENDATION, 'Рекомендации'),
        (TREND, 'Анализ трендов'),
        (CLUSTERING, 'Кластеризация'),
        (SUMMARY, 'Суммаризация'),
    )

    query_template = models.CharField(
        'Шаблон запроса'
    )
    template = models.ForeignKey(
        'Template',
        on_delete=models.CASCADE,
        related_name='meta_blocks',
        verbose_name='Шаблон отчета'
    )
    type = models.CharField(
        'Тип',
        choices=TYPES
    )
    position = models.PositiveIntegerField(
        'Позиция'
    )
    data_sources = models.ManyToManyField(
        'DataSource',
        blank=True,
        verbose_name='Источники данных'
    )
    filters = models.JSONField(
        'Фильтры',
        default=dict,
        blank=True,
        help_text='JSON с настройками фильтрации (домены, даты, языки и т.д.)'
    )
    processing_params = models.JSONField(
        'Параметры обработки',
        default=dict,
        blank=True,
        help_text='Параметры для AI/ML обработки'
    )

    class Meta:
        verbose_name = 'Мета-блок отчета'
        verbose_name_plural = 'Мета-блоки отчетов'

    def __str__(self) -> str:
        return self.query_template


class Report(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='reports',
        verbose_name='Пользователь',
        null=True
    )
    search_query = models.ForeignKey(
        'SearchQuery',
        on_delete=models.SET_NULL,
        related_name='reports',
        verbose_name='Поисковый запрос',
        null=True
    )
    template = models.ForeignKey(
        'Template',
        on_delete=models.SET_NULL,
        verbose_name='Шаблон',
        null=True
    )
    date = models.DateTimeField(
        auto_now_add=True
    )
    data = models.ManyToManyField(
        'Data',
        through='ReportBlock',
        verbose_name='Данные',
        related_name='reports'
    )
    search_start = models.DateField(
        null=True
    )
    search_end = models.DateField(
        null=True
    )

    class Meta:
        verbose_name = 'Аналитический отчет'
        verbose_name_plural = 'Аналитические отчеты'
        ordering = ('-pk',)

    def get_pdf(self):
        blocks = self.blocks.filter(readiness=ReportBlock.READY)
        if not blocks:
            return
        new_blocks, tables = preprocess_blocks(blocks)
        filename = f'report_{self.pk}.pdf'
        title = self.search_query
        save_pdf_report(title, new_blocks, tables, filename)
        with open(filename, 'rb') as f:
            content = ContentFile(f.read())
        return content

    def get_word(self):
        blocks = self.blocks.filter(readiness=ReportBlock.READY)
        if not blocks:
            return
        new_blocks, tables = preprocess_blocks(blocks)
        filename = f'report_{self.pk}.docx'
        save_word_report(new_blocks, filename)
        with open(filename, 'rb') as f:
            content = ContentFile(f.read())
        return content

    def get_excel(self):
        blocks = self.blocks.filter(readiness=ReportBlock.READY)
        if not blocks:
            return
        new_blocks, tables = preprocess_blocks(blocks)
        filename = f'report_{self.pk}.xlsx'
        save_excel_report(tables, filename)
        with open(filename, 'rb') as f:
            content = ContentFile(f.read())
        return content

class ReportBlock(models.Model):
    READY = 'ready'
    NOT_READY = 'not_ready'
    ERROR = 'error'
    READINESS_STATUSES = (
        (READY, 'Готов'),
        (NOT_READY, 'Не готов'),
        (ERROR, 'Ошибка')
    )

    PLOTLY = 'plotly'
    TEXT = 'text'
    TYPES = (
        (PLOTLY, 'Plotly'),
        (TEXT, 'Текст')
    )

    report = models.ForeignKey(
        'Report',
        on_delete=models.CASCADE,
        related_name='blocks',
        verbose_name='Отчет'
    )
    data = models.ForeignKey(
        'Data',
        on_delete=models.SET_NULL,
        related_name='report_blocks',
        verbose_name='Данные',
        null=True
    )
    representation = models.JSONField('Представление')
    type = models.CharField(
        'Тип',
        choices=TYPES
    )
    comment = models.TextField(
        'Комментарий',
        blank=True
    )
    summary = models.TextField(
        'Вывод LLM',
        blank=True
    )
    readiness = models.CharField(
        'Готовность',
        choices=READINESS_STATUSES
    )
    position = models.PositiveIntegerField(
        'Позиция'
    )


class Data(models.Model):
    WEB_PAGE = 'web_page'
    VIDEO = 'video'
    FILE = 'file'

    SOURCE_TYPES = (
        (WEB_PAGE, 'Страница в интернете'),
        (VIDEO, 'Видео'),
        (FILE, 'Пользовательский файл'),
    )

    # SERIES = 'series'
    # REFERENCE = 'reference'
    TEXT = 'text'
    PLOTLY = 'plotly'

    DATA_TYPES = (
        (PLOTLY, 'plotly'),
        # (SERIES, 'Временной ряд'),
        # (REFERENCE, 'Справочник'),
        (TEXT, 'Текст')
    )

    index_id = models.CharField(
        unique=True,
    )
    type = models.CharField(
        'Тип источника данных',
        choices=SOURCE_TYPES,
    )
    page = models.ForeignKey(
        'WebPage',
        on_delete=models.SET_NULL,
        related_name='data',
        verbose_name='Интернет страницы',
        null=True
    )
    file = models.ForeignKey(
        'Files',
        on_delete=models.SET_NULL,
        related_name='data',
        verbose_name='Пользовательский файл',
        null=True
    )
    data_type = models.CharField(
        'Тип данных',
        choices=DATA_TYPES,
        # max_length=16
    )
    meta_data = models.JSONField(
        verbose_name='Мета данные'
    )
    data = models.JSONField(
        verbose_name='Данные'
    )
    date = models.DateTimeField(
        'Дата создания версии',
    )
    version = models.PositiveIntegerField(
        'Версия'
    )

    class Meta:
        verbose_name = 'Данные'
        verbose_name_plural = 'Данные'


class WebPage(models.Model):
    url = models.CharField(
        'URL',
        max_length=1024,
        unique=True
    )
    title = models.CharField(
        'Title'
    )
    content = models.TextField(
        'Содержание страницы',
        blank=True
    )
    update_date = models.DateTimeField(
        'Дата обновления',
        null=True
    )

    class Meta:
        verbose_name = 'Интернет страница'
        verbose_name_plural = 'Интернет страницы'

    def __str__(self) -> str:
        return self.url


class Files(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='files',
        verbose_name='Пользователь',
        null=True
    )
    name = models.CharField(
        'Название файла'
    )
    file = models.FileField(
        upload_to='files/'
    )

    class Meta:
        verbose_name = 'Файл пользователя'
        verbose_name_plural = 'Пользовательские файлы'


class DataSource(models.Model):
    """Регистр доступных источников данных для TITAN Analytics"""
    WEB = 'web'
    PDF = 'pdf'
    VIDEO = 'video'
    API = 'api'
    DATABASE = 'database'
    FILE = 'file'
    SOCIAL = 'social'
    NEWS = 'news'
    
    SOURCE_TYPES = (
        (WEB, 'Веб-страница'),
        (PDF, 'PDF документ'),
        (VIDEO, 'Видео'),
        (API, 'API'),
        (DATABASE, 'База данных'),
        (FILE, 'Файл (CSV/Excel)'),
        (SOCIAL, 'Социальные сети'),
        (NEWS, 'Новостные агрегаторы'),
    )
    
    name = models.CharField(
        'Название',
        max_length=200
    )
    source_type = models.CharField(
        'Тип источника',
        max_length=20,
        choices=SOURCE_TYPES
    )
    base_url = models.URLField(
        'Базовый URL',
        blank=True
    )
    api_key_required = models.BooleanField(
        'Требуется API ключ',
        default=False
    )
    is_active = models.BooleanField(
        'Активен',
        default=True
    )
    config = models.JSONField(
        'Конфигурация',
        default=dict,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Источник данных'
        verbose_name_plural = 'Источники данных'
    
    def __str__(self) -> str:
        return self.name


class TemplateCategory(models.Model):
    """Категории шаблонов для различных use-cases"""
    name = models.CharField(
        'Название',
        max_length=200
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )
    icon = models.CharField(
        'Иконка',
        max_length=50,
        blank=True
    )
    description = models.TextField(
        'Описание',
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name='Родительская категория'
    )
    position = models.PositiveIntegerField(
        'Позиция',
        default=0
    )
    
    class Meta:
        verbose_name = 'Категория шаблона'
        verbose_name_plural = 'Категории шаблонов'
        ordering = ['position', 'name']
    
    def __str__(self) -> str:
        return self.name


class UserPreferences(models.Model):
    """Пользовательские настройки и предпочтения"""
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name='Пользователь'
    )
    favorite_templates = models.ManyToManyField(
        'Template',
        blank=True,
        related_name='favorited_by',
        verbose_name='Избранные шаблоны'
    )
    default_theme = models.ForeignKey(
        'Theme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Тематика по умолчанию'
    )
    default_ai_model = models.CharField(
        'AI модель по умолчанию',
        max_length=50,
        default='yandexgpt',
        choices=(
            ('yandexgpt', 'YandexGPT'),
            ('yandexgpt-lite', 'YandexGPT Lite'),
        )
    )
    settings = models.JSONField(
        'Настройки',
        default=dict,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Пользовательские настройки'
        verbose_name_plural = 'Пользовательские настройки'
    
    def __str__(self) -> str:
        return f'Настройки {self.user.username}'
