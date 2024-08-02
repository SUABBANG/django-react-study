import datetime
import json
from io import BytesIO
from typing import Literal
from urllib.request import urlopen

import pandas as pd
from django.conf import settings
from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404

from hottrack.models import Song
from hottrack.utils.cover import make_cover_image
from django.views.generic import DetailView, ListView, YearArchiveView, MonthArchiveView, DayArchiveView, \
    TodayArchiveView, WeekArchiveView, ArchiveIndexView, DateDetailView


class IndexView(ListView):
    model = Song
    template_name = "hottrack/index.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        release_date = self.kwargs.get("release_date")
        if release_date:
            qs = qs.filter(release_date=release_date)

        query = self.request.GET.get("query", "").strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(artist_name__icontains=query)
                | Q(album_name__icontains=query)
            )

        return qs

index = IndexView.as_view()

# def index(request: HttpRequest, release_date: datetime.date=None) -> HttpResponse:
#     query = request.GET.get("query", "").strip()
#     song_qs: QuerySet = Song.objects.all()
#     if release_date:
#         song_qs = song_qs.filter(release_date=release_date)
#
#     if query:
#         song_qs = song_qs.filter(
#             Q(name__icontains=query)
#             | Q(artist_name__icontains=query)
#             | Q(album_name__icontains=query)
#         )
#         print(song_qs)
#     return render(
#         request=request,
#         template_name="hottrack/index.html",
#         context={"song_list": song_qs, "query": query},
#     )


def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response


def export_csv(request: HttpRequest) -> HttpResponse:
    song_qs: QuerySet = Song.objects.all()

    # .values() : 지정한 필드로 구성된 사전 리스트를 반환
    song_qs = song_qs.values()
    # 원하는 필드만 지정해서 뽑을 수도 있습니다.
    # song_qs = song_qs.values("rank", "name", "artist_name", "like_count")

    # 사전 리스트를 인자로 받아서, DataFrame을 생성할 수 있습니다.
    df = pd.DataFrame(data=song_qs)

    # 메모리 파일 객체에 CSV 데이터를 저장합니다.
    # CSV를 HttpResponse에 바로 저장할 때 utf-8-sig 인코딩이 적용되지 않아서
    # BytesIO를 사용해서 인코딩을 적용한 후, HttpResponse에 저장합니다.
    export_file = BytesIO()

    # df.to_csv("hottrack.csv", index=False)      # 지정 파일로 저장할 수도 있고, 파일 객체를 전달할 수도 있습니다.
    # (한글깨짐방지) 한글 엑셀에서는 CSV 텍스트 파일을 해석하는 기본 인코딩이 cp949이기에
    # utf-8-sig 인코딩을 적용하여 생성되는 CSV 파일에 UTF-8 BOM이 추가합니다.
    df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")  # noqa

    # 저장된 파일의 전체 내용을 HttpResponse에 전달합니다.
    response = HttpResponse(content=export_file.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="hottrack.csv"'

    return response


def export(request: HttpRequest, format: Literal["csv", "xlsx"]) -> HttpResponse:
    song_qs: QuerySet = Song.objects.all()
    song_qs = song_qs.values()
    df = pd.DataFrame(data=song_qs)

    export_file = BytesIO()

    if format == "csv":
        content_type = "text/csv"
        filename = "hottrack.csv"
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")  # noqa
    elif format == "xlsx":
        # .xls : application/vnd.ms-excel
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # xlsx
        )
        filename = "hottrack.xlsx"
        df.to_excel(excel_writer=export_file, index=False, engine="openpyxl")  # noqa
    else:
        return HttpResponseBadRequest(f"Invalid format : {format}")

    response = HttpResponse(content=export_file.getvalue(), content_type=content_type)
    response["Content-Disposition"] = "attachment; filename*=utf-8''{}".format(filename)

    return response

# song_detail = DetailView.as_view(
#     model=Song,
#     slug_field="melon_uid",
#     slug_url_kwarg="melon_uid",
# )
class SongDetailView(DetailView):
    model = Song

    def get_object(self, queryset=None):
        # melon uid 인자가 있으면 사용하고 없으면 기본 구현으로
        if queryset is None:
            queryset = self.get_queryset()

        melon_uid = self.kwargs.get("melon_uid")
        if melon_uid:
            return get_object_or_404(queryset, melon_uid=melon_uid)

        return super().get_object(queryset)


song_detail = SongDetailView.as_view()

class SongYearArchiveView(YearArchiveView):
    model = Song
    date_field = "release_date"  # 조회할 날짜 필드

class SongMonthArchiveView(MonthArchiveView):
    model = Song
    # paginate_by = None
    date_field = "release_date"
    # 날짜 포맷 : "%m" (숫자, ex: "01", "1" 등), "%b" (디폴트, 월 이름의 약어, ex: "Jan", "Feb" 등)
    month_format = "%m"

class SongDayArchiveView(DayArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"

class SongTodayArchiveView(TodayArchiveView):
    model = Song
    date_field = "release_date"

    # DEBUG=True 에서만 get_dated_items 메서드를 재정의합니다.
    # 오늘 날짜 데이터를 조회할 때, 테스트를 위해 가짜 오늘 날짜를 지원하겠습니다.
    if settings.DEBUG:

        def get_dated_items(self):
            """지정 날짜의 데이터를 조회"""
            fake_today = self.request.GET.get("fake-today", "")
            try:
                year, month, day = map(int, fake_today.split("-", 3))
                return self._get_dated_items(datetime.date(year, month, day))
            except ValueError:
                # fake_today 파라미터가 없거나 날짜 형식이 잘못되었을 경우
                return super().get_dated_items()

class SongWeekArchiveView(WeekArchiveView):
    model = Song
    date_field = "release_date"
    # date_list_period = "week"
    # 템플릿 필터 date의 "W" 포맷은 ISO 8601에 따라 한 주의 시작을 월요일로 간주합니다.
    #  - 템플릿 단에서 한 주의 시작을 일요일로 할려면 커스텀 템플릿 태그 구현이 필요합니다.
    week_format = "%W"  # "%U" (디폴트, 한 주의 시작을 일요일), %W (한 주의 시작을 월요일)

# year 단위로 모든 year의 date_list를 뽑습니다.
class SongArchiveIndexView(ArchiveIndexView):
    model = Song
    # queryset = Song.objects.all()
    date_field = "release_date"  # 기준 날짜 필드
    paginate_by = 10

    # date_list_period = "year"  # 단위 : year (디폴트), month, day, week
    def get_date_list_period(self):
        # URL Captured Value에 date_list_period가 없으면, date_list_period 속성을 활용합니다.
        return self.kwargs.get("date_list_period", self.date_list_period)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["date_list_period"] = self.get_date_list_period()

class SongDateDetailView(DateDetailView):
    model = Song
    date_field = "release_date"
    month_format = "%m"