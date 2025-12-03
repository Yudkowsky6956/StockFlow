import logging
import webbrowser
from threading import Timer

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from i18n import t
from loguru import logger

from src.core.global_config import DEBUG
from src.interface.file_dialog import select_scv
from .core_script import InfographicsScripts

logging.getLogger('werkzeug').setLevel(logging.ERROR)   # HTTP запросы
logging.getLogger('dash').setLevel(logging.CRITICAL)    # Dash runtime
logging.getLogger('dash._callback').setLevel(logging.CRITICAL)
app = Dash(__name__)


class BasicGraph:
    media_type_map = {
        "photos": "info.scripts.show_sales_data.photos",
        "videos": "info.scripts.show_sales_data.videos",
        "vectors": "info.scripts.show_sales_data.vectors",
        "illustrations": "info.scripts.show_sales_data.illustrations"
    }
    media_ai_map = {
        True: "info.scripts.show_sales_data.ai",
        False: "info.scripts.show_sales_data.not_ai"
    }

    @classmethod
    def get_types_label(cls, row):
        return f"{t(cls.media_type_map[row['media_type']])}{t(cls.media_ai_map[row['media_ai_flag']])}"


class IncomeByTypePie(BasicGraph):
    def __init__(self, df):
        self.raw_df = df.copy()
        self.data = self.prepare_data()
        self.total_income = self.data['sell_income_num'].sum()
        self.figure = px.pie(
            self.data,
            names='label',
            values='sell_income_num',
            title=f"{t('info.scripts.show_sales_data.by_media_type')} — {self.total_income:,.2f}$",
            custom_data=["sales_count"]
        )
        self.figure.update_traces(
            textinfo='label+percent+value',
            texttemplate='%{label}: $%{value:,.1f} (%{percent})',
            hovertemplate=(
                    t("info.scripts.show_sales_data.sale_type") + ': %{label}<br>' +
                    t("info.scripts.show_sales_data.sale_income") + ': $%{value:,.1f}<br>' +
                    t("info.scripts.show_sales_data.sale_percent") + ': %{percent}<br>' +
                    t("info.scripts.show_sales_data.sale_amount") + ': %{customdata[0]}<extra></extra>'
            )
        )
        self.figure.update_layout(width=600, height=600)

    def prepare_data(self):
        data = self.raw_df.copy()
        data['sell_income_num'] = data['sell_income'].replace(r'[\$,]', '', regex=True).astype(float)
        grouped = data.groupby(['media_type', 'media_ai_flag'], as_index=False).agg(
            sell_income_num=('sell_income_num', 'sum'),
            sales_count=('sell_income_num', 'count')
        )
        total_income = grouped['sell_income_num'].sum()
        grouped['percent'] = grouped['sell_income_num'] / total_income * 100
        grouped['label'] = grouped.apply(self.get_types_label, axis=1)
        return grouped

    @property
    def layout(self):
        return dcc.Graph(id="income_by_type_pie", figure=self.figure)
        

class MediaByIncomeBars(BasicGraph):
    def __init__(self, df, media_type, media_ai_flag):
        self.raw_df = df.copy()
        self.media_type = media_type
        self.media_ai_flag = media_ai_flag
        self.id = f"media_by_income_bars_{self.media_type}_{self.media_ai_flag}"
        self.img_id = f"{self.id}_preview"
        self.data = self.prepare_data()

        if len(self.data) <= 20:
            self.orientation = 'h'
            x, y, text_pos = 'total_income', 'media_id', 'auto'
        else:
            self.orientation = 'v'
            x, y, text_pos = 'media_id', 'total_income', 'outside'

        label = self.get_types_label({"media_type": media_type, "media_ai_flag": media_ai_flag})
        self.figure = px.bar(
            self.data,
            x=x,
            y=y,
            orientation=self.orientation,
            text='text_label',
            custom_data=["media_id", "total_income", "pct_of_total", "media_preview", "media_link", "sales_count"],
            labels={'total_income': t("info.scripts.show_sales_data.sale_income") + ' ($)', 'media_id': t("info.scripts.show_sales_data.media_id")},
            title=t("info.scripts.show_sales_data.income_by") + f" {label}"
        )
        self.figure.update_traces(
            texttemplate='%{text}',
            hovertemplate=(
                t("info.scripts.show_sales_data.media_id") + ': %{customdata[0]}<br>' +
                t("info.scripts.show_sales_data.sale_income") + ': $%{customdata[1]:,.1f}<br>' +
                t("info.scripts.show_sales_data.sale_percent") + ': %{customdata[2]:.1f}%<br>' +
                t("info.scripts.show_sales_data.sale_amount") + ': %{customdata[5]}<br><extra></extra>'
            )
        )

        if self.orientation == 'h':
            self.figure.update_layout(yaxis={'categoryorder': 'total descending'}, height=600)
        else:
            self.figure.update_layout(xaxis={'categoryorder': 'total descending', 'tickangle': -45}, height=800)

        self.register_callbacks(app)

    def prepare_data(self):
        data = self.raw_df.copy()
        data['media_ai_flag'] = data['media_ai_flag'].astype(bool)
        data['sell_income_num'] = data['sell_income'].replace(r'[\$,]', '', regex=True).astype(float)
        data = data[(data['media_type'] == self.media_type) & (data['media_ai_flag'] == self.media_ai_flag)].copy()
        if data.empty:
            return None

        grouped = data.groupby(['media_id', 'media_preview'], as_index=False)['sell_income_num'].sum()
        grouped = grouped.rename(columns={'sell_income_num': 'total_income'})
        links = data.groupby('media_id', as_index=False)['media_link'].first()
        grouped = grouped.merge(links, on='media_id', how='left')
        sales_count = data.groupby('media_id', as_index=False).size().rename(columns={'size': 'sales_count'})
        grouped = grouped.merge(sales_count, on='media_id', how='left')
        grouped['media_id'] = grouped['media_id'].astype(str)
        grouped['pct_of_total'] = grouped['total_income'] / grouped['total_income'].sum() * 100
        grouped['text_label'] = grouped['total_income'].round(1).astype(str)
        return grouped

    @staticmethod
    def get_all_figures(df):
        figures = []
        existing_combinations = df.groupby(['media_type', 'media_ai_flag']).size().reset_index()[
            ['media_type', 'media_ai_flag']]
        for _, row in existing_combinations.iterrows():
            media_type = row['media_type']
            ai_flag = row['media_ai_flag']
            figure = MediaByIncomeBars(df, media_type, ai_flag)
            figures.append(figure)
        return figures

    def register_callbacks(self, app):
        @app.callback(
            Output(self.img_id, "src"),
            Output(self.img_id, "style"),
            Input(self.id, "hoverData")
        )
        def update_image(hoverData):
            if hoverData is None:
                return "", {"display": "none"}
            img_url = hoverData["points"][0]["customdata"][3]
            return img_url, {"display": "block", "maxWidth": "500px"}

        @app.callback(
            Output(self.id, "clickData"),
            Input(self.id, "clickData")
        )
        def open_link(clickData):
            if clickData is None:
                return None
            link = clickData["points"][0]["customdata"][4]
            if link:
                webbrowser.open(link)
            return None

    @property
    def layout(self):
        return html.Div([
            dcc.Graph(id=self.id, figure=self.figure),
            html.Img(id=self.img_id, src="", style={"maxWidth": "200px", "display": "none"})
        ])


class ShowSalesData(InfographicsScripts):
    @classmethod
    async def _run(cls):
        try:
            sales_file = select_scv()
        except RuntimeError as e:
            logger.error(e)
            return
    
        df = pd.read_csv(sales_file, header=0, sep=",")
        app.title = sales_file.name
    
        # === Построение интерфейса ===
        layout = [IncomeByTypePie(df).layout]
        for bar in MediaByIncomeBars.get_all_figures(df):
            layout.append(bar.layout)
    
        port = 8050
        Timer(1, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
        app.layout = html.Div(layout)
        app.run(port=port, debug=DEBUG)