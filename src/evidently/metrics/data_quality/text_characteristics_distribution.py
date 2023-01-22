from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import dataclasses

from evidently.metrics.base_metric import InputData
from evidently.metrics.base_metric import Metric
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import WidgetSize
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.render_utils import get_distribution_plot_figure
from evidently.utils.data_operations import process_columns
from evidently.utils.data_operations import recognize_column_type
from evidently.utils.visualizations import Distribution
from evidently.utils.visualizations import get_distribution_for_column
from evidently.features.non_letter_character_percentage_feature import NonLetterCharacterPercentage
from evidently.features.OOV_words_percentage_feature import OOVWordsPercentage
from evidently.features.text_length_feature import TextLength
from evidently.utils.data_preprocessing import DataDefinition
from evidently.utils.data_preprocessing import ColumnType


@dataclasses.dataclass
class TextCharacteristicsDistributionResult:
    column_name: str
    current: Dict[str, Distribution]
    reference: Optional[Dict[str, Distribution]] = None

class TextCharacteristicsDistribution(Metric[TextCharacteristicsDistributionResult]):
    """Calculates distribution for the column"""

    column_name: str
    generated_text_features: Optional[
        Dict[str, Union[TextLength, NonLetterCharacterPercentage, OOVWordsPercentage]]
    ]

    def __init__(
        self,
        column_name: str
    ) -> None:
        self.column_name = column_name
        self.text_features_gen = None
    
    def required_features(self, data_definition: DataDefinition):
        column_type = data_definition.get_column(self.column_name).column_type
        if column_type == ColumnType.Text:
            self.generated_text_features = {}
            self.generated_text_features["Text Length"] = TextLength(self.column_name)
            self.generated_text_features["Non Letter Character %"] = NonLetterCharacterPercentage(self.column_name)
            self.generated_text_features["OOV %"] = OOVWordsPercentage(self.column_name)
            return list(self.generated_text_features.values())
        return []

    def get_parameters(self) -> tuple:
        return (self.column_name)

    def calculate(self, data: InputData) -> TextCharacteristicsDistributionResult:
        current_results = {}
        reference_results = None
        if data.reference_data is not None:
            reference_results = {}
        if self.column_name not in data.current_data:
            raise ValueError(f"Column '{self.column_name}' was not found in current data.")

        if data.reference_data is not None:
            if self.column_name not in data.reference_data:
                raise ValueError(f"Column '{self.column_name}' was not found in reference data.")

        columns = process_columns(data.current_data, data.column_mapping)
        column_type = recognize_column_type(dataset=data.current_data, column_name=self.column_name, columns=columns)
        if column_type != "text":
            raise ValueError("Text column expected")
        for key, val in self.generated_text_features.items():
            current_column = data.get_current_column(val.feature_name())
            reference_column = None
            if data.reference_data is not None:
                reference_column = data.get_reference_column(val.feature_name())
            current, reference = get_distribution_for_column(
                column_type="num",
                current=current_column,
                reference=reference_column,
            )
            current_results[key] = current
            if data.reference_data is not None:
                reference_results[key] = reference

        return TextCharacteristicsDistributionResult(
            column_name=self.column_name,
            current=current_results,
            reference=reference_results,
        )


@default_renderer(wrap_type=TextCharacteristicsDistribution)
class TextCharacteristicsDistributionRenderer(MetricRenderer):
    def render_json(self, obj: TextCharacteristicsDistribution) -> dict:
        result = dataclasses.asdict(obj.get_result())
        result.pop("current", None)
        result.pop("reference", None)
        return result

    def render_html(self, obj: TextCharacteristicsDistribution) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        result = [
            header_text(label=f"Distribution for column '{metric_result.column_name}'.")
        ]
        for col in list(metric_result.current.keys()):
            distr_fig = get_distribution_plot_figure(
                current_distribution=metric_result.current[col],
                reference_distribution=metric_result.reference[col],
                color_options=self.color_options,
            )
            result.append(plotly_figure(title=col, figure=distr_fig, size=WidgetSize.FULL))

        return result
