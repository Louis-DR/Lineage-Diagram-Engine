import datetime
from typing import List, Optional, Dict, Any
from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.bundle import Bundle
from lineage_diagram.orbit import Orbit
from lineage_diagram.paths import MembershipEventType

DIAGRAM_WIDTH  = 12975.0
DIAGRAM_HEIGHT = 635
YEAR_GRID_INTERVAL_YEARS = 5
YEAR_GRID_COLOR = '#000000'
YEAR_GRID_OPACITY = 0.06
YEAR_GRID_STROKE_WIDTH = 2
YEAR_LABEL_ROTATION_DEGREES = -90
YEAR_LABEL_FONT_SIZE = '10px'
YEAR_LABEL_OPACITY = 0.12
YEAR_LABEL_FONT_FAMILY = 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif'
YEAR_LABEL_FONT_WEIGHT = '900'
YEAR_LABEL_X_OFFSET_PX = 0
YEAR_LABEL_Y_OFFSET_PX = 10
YEAR_LABEL_Y_SPACING_PX = 150
YEAR_LABEL_MARGIN_PX = 8
YEAR_LABEL_FONT_SIZE_PX = 10
YEAR_LABEL_CHAR_WIDTH_PX = 6.5
YEAR_LABEL_BG_COLOR = '#FFFFFF'
YEAR_LABEL_BG_OPACITY = 0.95
YEAR_LABEL_BG_PADDING_PX = 3
YEAR_LABEL_BG_RADIUS_PX = 2
DIAGRAM_START_DATE_YEAR = 1789

class PoliticalDiagram(Diagram):
    def __init__(self, view_width: float, view_height: float, resolution: int = 1000):
        super().__init__(view_width, view_height, resolution)
        self.overlays = []

    def add_overlay(self, svg_content: str):
        self.overlays.append(svg_content)

    def generate(self, filepath: str = 'diagram.svg'):
        super().generate(filepath)
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            svg_start_index = -1
            for i, line in enumerate(lines):
                if '<svg' in line:
                    svg_start_index = i
                    break
            if svg_start_index != -1:
                overlay_content = '\n'.join(self.overlays) + '\n'
                lines.insert(svg_start_index + 1, overlay_content)
                with open(filepath, 'w') as f:
                    f.writelines(lines)
        except Exception as e:
            print(f'Error injecting overlays: {e}')

def add_year_grid(diagram: PoliticalDiagram):
  start_date_year = DIAGRAM_START_DATE_YEAR
  first_year_multiple = ((start_date_year + (YEAR_GRID_INTERVAL_YEARS - 1)) // YEAR_GRID_INTERVAL_YEARS) * YEAR_GRID_INTERVAL_YEARS
  current_year = first_year_multiple
  end_year = datetime.date.today().year
  # Simplified date_to_x for grid (assuming linear scale from start)
  DIAGRAM_DATE_SCALE = 0.15
  START_DATE = datetime.date(1789, 7, 14)
  def date_to_x_grid(year):
      d = datetime.date(year, 1, 1)
      days = (d - START_DATE).days
      return float(days) * DIAGRAM_DATE_SCALE

  while current_year <= end_year:
    year_x = date_to_x_grid(current_year)
    diagram.add_overlay(
      f'<line x1="{year_x}" y1="0" x2="{year_x}" y2="{DIAGRAM_HEIGHT}" '
      f'stroke="{YEAR_GRID_COLOR}" stroke-width="{YEAR_GRID_STROKE_WIDTH}" stroke-opacity="{YEAR_GRID_OPACITY}"/>'
    )
    label_text = f"{current_year}"
    label_x = year_x + YEAR_LABEL_X_OFFSET_PX
    y_center = DIAGRAM_HEIGHT / 2.0
    def add_year_label_at(y_pos: float) -> bool:
      approx_text_width = len(label_text) * YEAR_LABEL_CHAR_WIDTH_PX
      rect_width = approx_text_width + 2 * YEAR_LABEL_BG_PADDING_PX
      rect_height = YEAR_LABEL_FONT_SIZE_PX + 2 * YEAR_LABEL_BG_PADDING_PX
      if (y_pos - rect_height / 2) < YEAR_LABEL_MARGIN_PX or (y_pos + rect_height / 2) > (DIAGRAM_HEIGHT - YEAR_LABEL_MARGIN_PX):
        return False
      rect_x = label_x - rect_width / 2
      rect_y = y_pos - rect_height / 2
      diagram.add_overlay(
        f'<rect x="{rect_x}" y="{rect_y}" width="{rect_width}" height="{rect_height}" '
        f'rx="{YEAR_LABEL_BG_RADIUS_PX}" ry="{YEAR_LABEL_BG_RADIUS_PX}" '
        f'fill="{YEAR_LABEL_BG_COLOR}" fill-opacity="{YEAR_LABEL_BG_OPACITY}" '
        f'transform="rotate({YEAR_LABEL_ROTATION_DEGREES} {label_x} {y_pos})"/>'
      )
      diagram.add_overlay(
        f'<text x="{label_x}" y="{y_pos}" fill="{YEAR_GRID_COLOR}" fill-opacity="{YEAR_LABEL_OPACITY}" '
        f'font-size="{YEAR_LABEL_FONT_SIZE}" font-family="{YEAR_LABEL_FONT_FAMILY}" font-weight="{YEAR_LABEL_FONT_WEIGHT}" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'style="font-variant-numeric: tabular-nums" '
        f'transform="rotate({YEAR_LABEL_ROTATION_DEGREES} {label_x} {y_pos})">{label_text}</text>'
      )
      return True
    add_year_label_at(y_center)
    step = YEAR_LABEL_Y_SPACING_PX
    offset_multiplier = 1
    while True:
      placed_any = False
      y_up = y_center - offset_multiplier * step
      y_down = y_center + offset_multiplier * step
      if y_up >= 0: placed_any = add_year_label_at(y_up) or placed_any
      if y_down <= DIAGRAM_HEIGHT: placed_any = add_year_label_at(y_down) or placed_any
      if not placed_any: break
      offset_multiplier += 1
    current_year += YEAR_GRID_INTERVAL_YEARS

diagram = PoliticalDiagram(view_width=DIAGRAM_WIDTH, view_height=DIAGRAM_HEIGHT, resolution=10000)
add_year_grid(diagram)
bundle_CONV_FED = Bundle(diagram, 12736.05, 327.5, 2.0)
bundle_UDF = Bundle(diagram, 10330.05, 357.5, 2.0)
lineage_FTSF_1 = Lineage(diagram, '#FF0000', 4919.4, 167.5, 6.0, z=6.0)
lineage_FTSF_1.terminate_at(6170.849999999999)
lineage_PSR_1 = Lineage(diagram, '#FF0000', 5037.599999999999, 117.5, 3.0, z=3.0)
lineage_PSR_1.terminate_at(6133.8)
lineage_FGSRI_1 = Lineage(diagram, '#FF0000', 5993.099999999999, 202.5, 2.0, z=2.0)
lineage_FGSRI_1.terminate_at(6139.2)
lineage_FSRI_1 = Lineage(diagram, '#FF0000', 5997.3, 212.5, 2.0, z=2.0)
lineage_FSRI_1.terminate_at(6139.2)
lineage_PRAD_1 = Lineage(diagram, '#C71982', 6132.45, 297.5, 6.0, z=42.397749152542374)
lineage_PRAD_1.terminate_at(12950.85)
lineage_PSN_1 = Lineage(diagram, '#FF0000', 7036.8, 277.5, 2.0, z=2.0)
lineage_PSN_1.terminate_at(7202.55)
lineage_PRS-1923_1 = Lineage(diagram, '#FF0000', 7327.65, 247.5, 6.0, z=6.0)
lineage_PRS-1923_1.terminate_at(7498.799999999999)
lineage_PAPF_1 = Lineage(diagram, '#255D32', 7580.549999999999, 437.5, 2.0, z=2.0)
lineage_PAPF_1.terminate_at(8527.949999999999)
lineage_PRS-1928_1 = Lineage(diagram, '#FF0000', 7606.95, 247.5, 2.0, z=2.0)
lineage_PRS-1928_1.terminate_at(8015.4)
lineage_CCI_1 = Lineage(diagram, '#770000', 8067.0, 77.5, 3.0, z=3.0)
lineage_CCI_1.terminate_at(8471.55)
lineage_DP_1 = Lineage(diagram, '#013502', 8724.15, 437.5, 2.0, z=2.0)
lineage_DP_1.terminate_at(12950.85)
lineage_CNIP_1 = Lineage(diagram, '#255D32', 8737.35, 437.5, 6.0, z=6.0)
lineage_CNIP_1.terminate_at(12950.85)
lineage_LO_1 = Lineage(diagram, '#770000', 9169.5, 37.5, 3.0, z=4.870496551724138)
lineage_LO_1.terminate_at(12950.85)
lineage_CIR_1 = Lineage(diagram, '#FF0000', 9582.6, 257.5, 2.0, z=2.0)
lineage_CIR_1.terminate_at(9966.3)
lineage_UCRG_1 = Lineage(diagram, '#FF0000', 9672.6, 242.5, 2.0, z=2.0)
lineage_UCRG_1.terminate_at(9864.6)
lineage_UGCS_1 = Lineage(diagram, '#FF0000', 9722.699999999999, 247.5, 2.0, z=2.0)
lineage_UGCS_1.terminate_at(9864.6)
lineage_RN_1 = Lineage(diagram, '#8A5928', 10038.3, 587.5, 6.0, z=23.542727774125648)
lineage_RN_1.terminate_at(12950.85)
lineage_MÉP_1 = Lineage(diagram, '#66C52C', 10153.05, 284.5, 2.0, z=2.0)
lineage_MÉP_1.terminate_at(10658.25)
lineage_RPF_1 = Lineage(diagram, '#021A6F', 10266.6, 462.5, 6.0, z=38.97415848921294)
lineage_RPF_1.terminate_at(11657.1)
lineage_CÉ_1 = Lineage(diagram, '#66C52C', 10291.8, 290.5, 2.0, z=2.0)
lineage_CÉ_1.terminate_at(10658.25)
lineage_NUDF_1 = Lineage(diagram, '#F07400', 11470.949999999999, 357.5, 6.0, z=10.343742151857231)
lineage_NUDF_1.terminate_at(11933.55)
lineage_RE_1 = Lineage(diagram, '#FFD600', 12421.65, 357.5, 6.0, z=42.37344288017236)
lineage_RE_1.terminate_at(12950.85)
lineage_PRAD_1.scale_to(6160.349999999999, 6201.75, 26.48569100169779)
lineage_PRAD_1.scale_to(6362.7, 6422.25, 34.61495510204082)
lineage_PRAD_1.scale_to(6598.2, 6639.599999999999, 42.397749152542374)
lineage_PRAD_1.scale_to(6746.25, 6787.05, 41.787749152542375)
lineage_PRAD_1.scale_to(6817.65, 6859.05, 33.780485049833885)
lineage_PRAD_1.scale_to(7120.2, 7170.599999999999, 25.55984730831974)
lineage_PRAD_1.scale_to(7365.75, 7411.799999999999, 34.13872876712329)
lineage_PRAD_1.scale_to(7583.25, 7624.349999999999, 33.306760784313724)
lineage_PRAD_1.scale_to(7749.45, 7790.849999999999, 32.196760784313724)
lineage_PRAD_1.scale_to(7803.599999999999, 7845.299999999999, 28.847102439024393)
lineage_PRAD_1.scale_to(8022.0, 8063.4, 26.10681941747573)
lineage_PRAD_1.scale_to(8182.2, 8223.3, 26.65681941747573)
lineage_PRAD_1.scale_to(8541.0, 8649.6, 23.65645550239234)
lineage_PRAD_1.scale_to(8850.6, 8891.699999999999, 25.496176076555024)
lineage_PRAD_1.scale_to(8988.6, 9029.699999999999, 25.506176076555025)
lineage_PRAD_1.scale_to(9099.6, 9140.699999999999, 24.097887539936103)
lineage_PRAD_1.scale_to(9259.199999999999, 9303.3, 22.378694300518134)
lineage_PRAD_1.scale_to(9477.6, 9518.4, 9.822293775933609)
lineage_PRAD_1.scale_to(9702.3, 9753.75, 4.975758533048061)
lineage_PRAD_1.scale_to(9784.199999999999, 9825.0, 4.517156364109377)
lineage_PRAD_1.scale_to(9969.3, 10010.4, 3.7585781820546886)
lineage_PRAD_1.scale_to(10041.3, 10082.4, 3.606550625411455)
lineage_PRAD_1.scale_to(10316.4, 10357.5, 3.8027310336048883)
lineage_PRAD_1.scale_to(10495.05, 10535.85, 3.239544289519035)
lineage_PRAD_1.scale_to(10754.25, 10795.35, 3.5742477926827605)
lineage_PRAD_1.scale_to(10877.25, 10918.05, 3.228039176171859)
lineage_PRAD_1.scale_to(11139.6, 11180.699999999999, 3.873001426786506)
lineage_PRAD_1.scale_to(11368.65, 11409.449999999999, 3.2144675727446868)
lineage_PRAD_1.scale_to(11644.8, 11685.6, 3.5752662877724313)
lineage_PRAD_1.scale_to(11918.699999999999, 11959.8, 4.150602638966562)
lineage_PRAD_1.scale_to(12192.9, 12233.699999999999, 3.5471667244367415)
lineage_PRAD_1.scale_to(12466.949999999999, 12507.75, 3.2459833622183707)
lineage_PRAD_1.scale_to(12551.25, 12597.449999999999, 2.1229916811091853)
lineage_PRAD_1.scale_to(12741.0, 12781.8, 2.3327722703639515)
lineage_PRAD_1.scale_to(12853.199999999999, 12894.3, 2.2127889081455807)
lineage_LO_1.scale_to(10041.3, 10082.4, 3.5496)
lineage_LO_1.scale_to(10106.25, 10147.65, 3.7826)
lineage_LO_1.scale_to(10316.4, 10357.5, 3.641)
lineage_LO_1.scale_to(10383.6, 10424.699999999999, 3.7641999999999998)
lineage_LO_1.scale_to(10488.449999999999, 10535.85, 3.6196)
lineage_LO_1.scale_to(10658.85, 10699.65, 3.5792)
lineage_LO_1.scale_to(10754.25, 10795.35, 3.464)
lineage_LO_1.scale_to(10871.699999999999, 10918.05, 3.2818)
lineage_LO_1.scale_to(10932.9, 10973.699999999999, 3.2561999999999998)
lineage_LO_1.scale_to(11139.6, 11180.699999999999, 3.7721999999999998)
lineage_LO_1.scale_to(11205.9, 11246.699999999999, 3.8058)
lineage_LO_1.scale_to(11254.949999999999, 11296.35, 4.136800000000001)
lineage_LO_1.scale_to(11368.65, 11409.449999999999, 4.5472)
lineage_LO_1.scale_to(11479.8, 11520.9, 4.870496551724138)
lineage_LO_1.scale_to(11638.199999999999, 11685.6, 4.2740965517241385)
lineage_LO_1.scale_to(11754.0, 11794.8, 3.9640000000000004)
lineage_LO_1.scale_to(11912.25, 11959.8, 3.4434)
lineage_LO_1.scale_to(12027.0, 12067.8, 3.3874)
lineage_LO_1.scale_to(12186.3, 12233.699999999999, 3.2264)
lineage_LO_1.scale_to(12298.65, 12340.05, 3.2252)
lineage_LO_1.scale_to(12460.35, 12507.75, 3.2836)
lineage_LO_1.scale_to(12572.699999999999, 12614.1, 3.2680000000000002)
lineage_LO_1.scale_to(12731.85, 12781.8, 3.3296)
lineage_LO_1.scale_to(12849.15, 12894.3, 3.3372)
lineage_RN_1.scale_to(10041.3, 10082.4, 6.3192)
lineage_RN_1.scale_to(10106.25, 10147.65, 6.3942)
lineage_RN_1.scale_to(10316.4, 10357.5, 6.1446000000000005)
lineage_RN_1.scale_to(10488.449999999999, 10535.85, 6.0432)
lineage_RN_1.scale_to(10658.85, 10699.65, 7.261940740740741)
lineage_RN_1.scale_to(10754.25, 10795.35, 10.990546633288401)
lineage_RN_1.scale_to(10871.699999999999, 10918.05, 11.01773519481353)
lineage_RN_1.scale_to(10932.9, 10973.699999999999, 11.008935194813532)
lineage_RN_1.scale_to(11139.6, 11180.699999999999, 11.629740740740742)
lineage_RN_1.scale_to(11205.9, 11246.699999999999, 11.599220689655173)
lineage_RN_1.scale_to(11254.949999999999, 11296.35, 11.660220689655173)
lineage_RN_1.scale_to(11368.65, 11409.449999999999, 12.306615143727964)
lineage_RN_1.scale_to(11479.8, 11520.9, 11.699622040279687)
lineage_RN_1.scale_to(11638.199999999999, 11685.6, 10.980027586206898)
lineage_RN_1.scale_to(11754.0, 11794.8, 11.36756756756757)
lineage_RN_1.scale_to(11912.25, 11959.8, 9.033567567567568)
lineage_RN_1.scale_to(12027.0, 12067.8, 8.651524324324324)
lineage_RN_1.scale_to(12186.3, 12233.699999999999, 11.673518778397113)
lineage_RN_1.scale_to(12298.65, 12358.65, 14.08191741151299)
lineage_RN_1.scale_to(12460.35, 12507.75, 14.575484135949733)
lineage_RN_1.scale_to(12572.699999999999, 12614.1, 14.163674898864546)
lineage_RN_1.scale_to(12646.5, 12687.3, 14.14068639311742)
lineage_RN_1.scale_to(12731.85, 12781.8, 18.743670448576687)
lineage_RN_1.scale_to(12810.15, 12894.3, 23.542727774125648)
lineage_RPF_1.scale_to(10316.4, 10357.5, 30.73197556008147)
lineage_RPF_1.scale_to(10383.6, 10424.699999999999, 32.49508667119258)
lineage_RPF_1.scale_to(10488.449999999999, 10535.85, 18.709897261823944)
lineage_RPF_1.scale_to(10658.85, 10699.65, 20.14826763219431)
lineage_RPF_1.scale_to(10754.25, 10795.35, 31.803866230181654)
lineage_RPF_1.scale_to(10871.699999999999, 10918.05, 21.08597714872585)
lineage_RPF_1.scale_to(10932.9, 10973.699999999999, 20.00345863020733)
lineage_RPF_1.scale_to(11139.6, 11180.699999999999, 37.05560421079659)
lineage_RPF_1.scale_to(11205.9, 11246.699999999999, 36.92615848921294)
lineage_RPF_1.scale_to(11254.949999999999, 11296.35, 38.97415848921294)
lineage_RPF_1.scale_to(11368.65, 11409.449999999999, 21.58114635749716)
lineage_RPF_1.scale_to(11479.8, 11520.9, 20.931215323014403)
lineage_RPF_1.scale_to(11638.199999999999, 11657.1, 9.427586206896553)
lineage_NUDF_1.scale_to(11638.199999999999, 11685.6, 8.973450259965338)
lineage_NUDF_1.scale_to(11754.0, 11794.8, 10.343742151857231)
lineage_NUDF_1.scale_to(11912.25, 11933.55, 9.227291891891891)
lineage_RE_1.scale_to(12460.35, 12522.449999999999, 40.56525047510907)
lineage_RE_1.scale_to(12572.699999999999, 12614.1, 42.37344288017236)
lineage_RE_1.scale_to(12731.85, 12781.8, 33.67108031518102)
lineage_RE_1.scale_to(12810.15, 12894.3, 29.12860727150386)
lineage_POF_1 = Lineage.create_from_lineage(lineage_FTSF_1, 5106.75, 5130.75, '#FF0000', 6.0, 127.5, z=6.0, new_in_bundle=None, new_index=-1)
lineage_CCSR_1 = Lineage.create_from_lineage(lineage_PSR_1, 5484.15, 5508.15, '#FF0000', 3.0, 287.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_POSR_1 = Lineage.create_from_lineage(lineage_FTSF_1, 5547.3, 5571.3, '#FF0000', 3.0, 142.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_ACR_1 = Lineage.create_from_lineage(lineage_POSR_1, 5873.099999999999, 5897.099999999999, '#FF0000', 2.0, 135.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_ACR_1.end_at_lineage(lineage_PSR_1, 5900.25, 5924.25)
lineage_PSdF_1 = Lineage.create_from_merge(diagram, '#FF0000', 6109.8, 6133.8, 122.5, 6.0, [lineage_PSR_1, lineage_POF_1], z=6.0)
lineage_FSR_1 = Lineage.create_from_merge(diagram, '#FF0000', 6115.2, 6139.2, 207.5, 3.0, [lineage_FGSRI_1, lineage_FSRI_1], z=3.0)
lineage_PSF_1 = Lineage.create_from_merge(diagram, '#FF0000', 6146.849999999999, 6170.849999999999, 187.5, 6.0, [lineage_FTSF_1, lineage_FSR_1], z=6.0)
lineage_SFIO_1 = Lineage.create_from_merge(diagram, '#FF0000', 6319.05, 6343.05, 147.5, 6.0, [lineage_PSdF_1, lineage_POSR_1, lineage_PSF_1], z=32.094693779904304)
split_res_SFIO_6448 = lineage_SFIO_1.split(6448.8, 6472.8, [{'color': '#FF0000', 'target_w': 9.731057142857143, 'target_y': 147.5, 'is_continuation': True, 'z': 32.094693779904304, 'in_assembly': None, 'index': -1}, {'color': '#FF0000', 'target_w': 4.5990244897959185, 'target_y': 247.5, 'is_continuation': False, 'z': 4.5990244897959185, 'in_assembly': None, 'index': -1}])
lineage_SFIO_2 = split_res_SFIO_6448[0]
lineage_PRS-1907_1 = split_res_SFIO_6448[1]
lineage_SFIO_2.shift_to(6819.0, 6873.75, 177.5)
lineage_PO-1914_1 = Lineage.create_from_lineage(lineage_SFIO_2, 6823.05, 6847.05, '#FF0000', 2.0, 137.5, z=2.0, new_in_bundle=None, new_index=-1)
split_res_PRS-1907_6824 = lineage_PRS-1907_1.split(6824.7, 6848.7, [{'color': '#FF0000', 'target_w': 3.0, 'target_y': 247.5, 'is_continuation': True, 'z': 4.5990244897959185, 'in_assembly': None, 'index': -1}, {'color': '#FF0000', 'target_w': 3.0, 'target_y': 257.5, 'is_continuation': False, 'z': 3.0, 'in_assembly': None, 'index': -1}])
lineage_PRS-1907_2 = split_res_PRS-1907_6824[0]
lineage_PRS-1914_1 = split_res_PRS-1907_6824[1]
lineage_PO-1914_1.end_at_lineage(lineage_SFIO_2, 7005.0, 7029.0)
lineage_SFIO_2.shift_to(7038.15, 7147.65, 147.5)
lineage_PSF-1920_1 = Lineage.create_from_lineage(lineage_SFIO_2, 7158.45, 7182.45, '#FF0000', 3.0, 227.5, z=3.0, new_in_bundle=None, new_index=-1)
split_res_SFIO_7202 = lineage_SFIO_2.split(7202.25, 7226.25, [{'color': '#FF0000', 'target_w': 7.725663295269168, 'target_y': 107.5, 'is_continuation': False, 'z': 31.748907177033495, 'in_assembly': None, 'index': -1}, {'color': '#FF0000', 'target_w': 12.902653181076673, 'target_y': 187.5, 'is_continuation': True, 'z': 32.094693779904304, 'in_assembly': None, 'index': -1}])
lineage_PCF_1 = split_res_SFIO_7202[0]
lineage_SFIO_3 = split_res_SFIO_7202[1]
lineage_UFS_1 = Lineage.create_from_lineage(lineage_PCF_1, 7300.95, 7324.95, '#FF0000', 2.0, 147.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_PCU_1 = Lineage.create_from_lineage(lineage_PCF_1, 7312.349999999999, 7336.349999999999, '#FF0000', 3.0, 147.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_PSC_1 = Lineage.create_from_merge(diagram, '#FF0000', 7305.9, 7329.9, 147.5, 3.0, [lineage_PCU_1], z=3.0)
lineage_UFS_1.end_at_lineage(lineage_PSC_1, 7305.9, 7329.9)
lineage_PSF-1929_1 = Lineage.create_from_merge(diagram, '#FF0000', 7474.799999999999, 7498.799999999999, 237.5, 6.0, [lineage_PSF-1920_1, lineage_PRS-1923_1], z=6.0)
conn_PSC_SFIO_1 = Lineage.create_from_lineage(lineage_PSC_1, 7572.15, 7596.15, '#FF0000', 2.0, 187.5, z=3.0)
conn_PSC_SFIO_1.end_at_lineage(lineage_SFIO_3, 7572.15, 7596.15)
lineage_POP_1 = Lineage.create_from_lineage(lineage_PCF_1, 7689.9, 7713.9, '#FF0000', 2.0, 137.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_PUP_1 = Lineage.create_from_merge(diagram, '#FF0000', 7724.7, 7748.7, 142.5, 3.0, [lineage_PSC_1], z=3.0)
lineage_POP_1.end_at_lineage(lineage_PUP_1, 7724.7, 7748.7)
lineage_GBL_1 = Lineage.create_from_lineage(lineage_PCF_1, 7748.7, 7772.7, '#770000', 3.0, 77.5, z=3.0, new_in_bundle=None, new_index=-1)
split_res_SFIO_7906 = lineage_SFIO_3.split(7906.2, 7930.2, [{'color': '#FF0000', 'target_w': 12.922931707317073, 'target_y': 187.5, 'is_continuation': True, 'z': 32.094693779904304, 'in_assembly': None, 'index': -1}, {'color': '#FF0000', 'target_w': 10.61528780487805, 'target_y': 257.5, 'is_continuation': False, 'z': 10.61528780487805, 'in_assembly': None, 'index': -1}])
lineage_SFIO_4 = split_res_SFIO_7906[0]
lineage_PSdF-UJJ_1 = split_res_SFIO_7906[1]
lineage_SFIO_4.shift_to(7914.75, 8024.25, 197.5)
lineage_PCF_1.shift_to(7914.75, 8024.25, 127.5)
lineage_PUP_1.shift_to(7914.75, 8024.25, 157.5)
lineage_JSR_1 = Lineage.create_from_lineage(lineage_SFIO_4, 8001.0, 8025.0, '#770000', 3.0, 77.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_USR_1 = Lineage.create_from_merge(diagram, '#FF0000', 7991.4, 8015.4, 247.5, 10.61528780487805, [lineage_PSF-1929_1, lineage_PSdF-UJJ_1], z=10.61528780487805)
lineage_PRS-1928_1.end_at_lineage(lineage_USR_1, 7991.4, 8015.4)
lineage_PRAS_1 = Lineage.create_from_lineage(lineage_PAPF_1, 8029.5, 8053.5, '#255D32', 2.0, 437.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_POR_1 = Lineage.create_from_merge(diagram, '#770000', 8015.549999999999, 8039.549999999999, 77.5, 3.0, [lineage_GBL_1, lineage_JSR_1], z=3.0)
lineage_POI_1 = Lineage.create_from_lineage(lineage_SFIO_4, 8047.2, 8071.2, '#770000', 3.0, 77.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_CCI_1.shift_to(8067.0, 8091.0, 72.49999999999997)
lineage_PUP_1.end_at_lineage(lineage_SFIO_4, 8059.65, 8083.65)
lineage_PSOP_1 = Lineage.create_from_lineage(lineage_SFIO_4, 8157.599999999999, 8181.599999999999, '#FF0000', 3.0, 167.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_PCF_1.shift_to(8188.65, 8298.3, 107.5)
lineage_GO_1 = Lineage.create_from_lineage(lineage_CCI_1, 8353.05, 8377.05, '#770000', 2.0, 62.50000000000003, z=2.0, new_in_bundle=None, new_index=-1)
lineage_SFIO_4.shift_to(8462.55, 8517.449999999999, 207.5)
lineage_PCI-1944_1 = Lineage.create_from_merge(diagram, '#770000', 8447.55, 8471.55, 57.5, 3.0, [lineage_CCI_1, lineage_POI_1], z=3.0)
lineage_GO_1.end_at_lineage(lineage_PCI-1944_1, 8447.55, 8471.55)
lineage_PPUS_1 = Lineage(diagram, '#255D32', 8527.949999999999, 437.5, 2.0, z=2.0)
lineage_PAPF_1.end_at_lineage(lineage_PPUS_1, 8503.949999999999, 8527.949999999999)
lineage_PRAD_1.shift_to(8572.199999999999, 9229.65, 312.5)
lineage_CNIP_2 = Lineage.create_from_merge(diagram, '#255D32', 8828.85, 8852.85, 437.5, 6.0, [lineage_CNIP_1, lineage_PPUS_1], z=6.0)
lineage_PRAD_1.shift_to(9229.65, 9996.6, 327.5)
split_res_CNIP_9499 = lineage_CNIP_2.split(9499.05, 9523.05, [{'color': '#002153', 'target_w': 3.0, 'target_y': 357.5, 'is_continuation': False, 'z': 3.0, 'in_assembly': None, 'index': -1}, {'color': '#255D32', 'target_w': 6.0, 'target_y': 437.5, 'is_continuation': True, 'z': 6.0, 'in_assembly': None, 'index': -1}])
lineage_RI_1 = split_res_CNIP_9499[0]
lineage_CNIP_3 = split_res_CNIP_9499[1]
lineage_PS_1 = Lineage.create_from_merge(diagram, '#E3265B', 9840.6, 9864.6, 207.5, 14.403217231046067, [lineage_SFIO_4], z=46.66617308011412)
lineage_UCRG_1.end_at_lineage(lineage_PS_1, 9840.6, 9864.6)
lineage_UGCS_1.end_at_lineage(lineage_PS_1, 9840.6, 9864.6)
lineage_PS_1.shift_to(9864.6, 9996.6, 197.5)
lineage_PCF_1.shift_to(9887.1, 9996.6, 127.5)
lineage_CIR_1.end_at_lineage(lineage_PS_1, 9942.3, 9966.3)
split_res_PRAD_9989 = lineage_PRAD_1.split(9989.85, 10013.85, [{'color': '#C71982', 'target_w': 3.7585781820546886, 'target_y': 257.5, 'is_continuation': False, 'z': 3.7585781820546886, 'in_assembly': None, 'index': -1}, {'color': '#C71982', 'target_w': 3.7585781820546886, 'target_y': 367.5, 'is_continuation': True, 'z': 42.397749152542374, 'in_assembly': None, 'index': -1}])
lineage_PRG-1971_1 = split_res_PRAD_9989[0]
lineage_PRAD_2 = split_res_PRAD_9989[1]
lineage_PRAD_2.shift_to(9996.6, 10051.5, 367.5)
lineage_PCF_1.shift_to(10489.8, 10654.05, 137.5)
lineage_PRG-1971_1.shift_to(10489.8, 10654.05, 277.5)
lineage_RN_1.shift_to(10544.55, 10763.699999999999, 582.5)
lineage_PS_1.shift_to(10599.3, 10654.05, 247.5)
lineage_LÉ_1 = Lineage.create_from_merge(diagram, '#66C52C', 10634.25, 10658.25, 287.5, 6.0, [lineage_MÉP_1, lineage_CÉ_1], z=6.0)
lineage_PCF_1.shift_to(11037.6, 11366.4, 187.5)
lineage_LÉ_1.shift_to(11202.0, 11256.75, 227.5)
lineage_PS_1.shift_to(11256.75, 11366.4, 267.5)
lineage_PRG-1971_1.shift_to(11256.75, 11366.4, 297.5)
lineage_LR_1 = Lineage.create_from_merge(diagram, '#0045B0', 11633.1, 11657.1, 462.5, 20.931215323014403, [lineage_RPF_1], z=52.309675959942126)
lineage_LR_1.shift_to(11859.449999999999, 12023.85, 497.5)
lineage_MoDem_1 = Lineage.create_from_merge(diagram, '#EF5222', 11909.55, 11933.55, 397.5, 11.51674215185723, [lineage_NUDF_1], z=22.298691722791393)
lineage_LFI_1 = Lineage.create_from_lineage(lineage_PS_1, 12018.9, 12042.9, '#CC2443', 3.0, 207.5, z=15.435480257990918, new_in_bundle=None, new_index=-1)
lineage_PRG-1971_1.shift_to(12188.1, 12462.15, 317.5)
lineage_PS_1.shift_to(12243.0, 12352.5, 287.5)
lineage_RN_1.shift_to(12243.0, 12462.15, 567.5)
lineage_ND_1 = Lineage.create_from_lineage(lineage_PS_1, 12292.65, 12316.65, '#C23089', 2.0, 245.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_PCF_1.shift_to(12352.5, 12516.9, 207.5)
lineage_LFI_1.shift_to(12352.5, 12516.9, 167.5)
lineage_PRAD_2.shift_to(12462.15, 12513.449999999999, 417.5)
lineage_PS_1.shift_to(12462.15, 12736.05, 257.5)
lineage_LR_1.shift_to(12487.35, 12761.4, 512.5)
lineage_G·s_1 = Lineage.create_from_lineage(lineage_PS_1, 12489.3, 12513.3, '#D9185D', 3.0, 237.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_GDS_1 = Lineage.create_from_lineage(lineage_PS_1, 12510.75, 12534.75, '#EE3437', 2.0, 187.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_Agir_1 = Lineage.create_from_lineage(lineage_LR_1, 12511.5, 12535.5, '#43519E', 3.0, 469.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_PRAD_3 = Lineage.create_from_merge(diagram, '#C71982', 12489.449999999999, 12513.449999999999, 417.5, 3.2459833622183707, [lineage_PRG-1971_1, lineage_PRAD_2], z=42.397749152542374)
lineage_RN_1.shift_to(12516.9, 12790.8, 557.5)
lineage_RE_1.shift_to(12516.9, 12736.05, 437.5)
lineage_PP_1 = Lineage.create_from_lineage(lineage_PS_1, 12563.25, 12587.25, '#FEF10A', 3.0, 282.5, z=3.0, new_in_bundle=var_1, new_index=-1)
split_res_PRAD_12577 = lineage_PRAD_3.split(12577.05, 12601.05, [{'color': '#C71982', 'target_w': 2.1229916811091853, 'target_y': 297.5, 'is_continuation': False, 'z': 2.1229916811091853, 'in_assembly': None, 'index': -1}, {'color': '#C71982', 'target_w': 2.1229916811091853, 'target_y': 464.5, 'is_continuation': True, 'z': 42.397749152542374, 'in_assembly': None, 'index': -1}])
lineage_PRG-2019_1 = split_res_PRAD_12577[0]
lineage_PRAD_4 = split_res_PRAD_12577[1]
lineage_TdP_1 = Lineage.create_from_lineage(lineage_PS_1, 12631.05, 12655.05, '#E1435E', 3.0, 377.5, z=3.0, new_in_bundle=None, new_index=-1)
lineage_EC_1 = Lineage.create_from_lineage(lineage_RE_1, 12669.449999999999, 12693.449999999999, '#DC6863', 2.0, 342.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_HOR_1 = Lineage.create_from_lineage(lineage_RE_1, 12723.449999999999, 12747.449999999999, '#0000BA', 6.0, 475.5, z=6.0, new_in_bundle=None, new_index=-1)
conn_Agir_HOR_1 = Lineage.create_from_lineage(lineage_Agir_1, 12723.449999999999, 12747.449999999999, '#43519E', 0.1, 475.5, z=3.0)
conn_Agir_HOR_1.end_at_lineage(lineage_HOR_1, 12723.449999999999, 12747.449999999999)
lineage_FP_1 = Lineage.create_from_lineage(lineage_PS_1, 12756.75, 12780.75, '#FB0057', 2.0, 367.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_CSDR_1 = Lineage.create_from_lineage(lineage_TdP_1, 12762.15, 12786.15, '#8307BD', 2.0, 377.5, z=2.0, new_in_bundle=None, new_index=-1)
lineage_CONV_1 = Lineage.create_from_lineage(lineage_PS_1, 12795.449999999999, 12819.449999999999, '#5D1354', 2.0, 327.5, z=2.0, new_in_bundle=bundle_CONV_FED, new_index=0)
lineage_L'A_1 = Lineage.create_from_lineage(lineage_LFI_1, 12866.699999999999, 12890.699999999999, '#F39E36', 3.0, 182.5, z=3.0, new_in_bundle=None, new_index=-1)
split_res_LR_12872 = lineage_LR_1.split(12872.699999999999, 12896.699999999999, [{'color': '#0045B0', 'target_w': 14.033975909214659, 'target_y': 512.5, 'is_continuation': True, 'z': 52.309675959942126, 'in_assembly': None, 'index': -1}, {'color': '#0045B0', 'target_w': 6.443132532520568, 'target_y': 557.5, 'is_continuation': False, 'z': 6.443132532520568, 'in_assembly': var_2, 'index': 1}])
lineage_LR_2 = split_res_LR_12872[0]
lineage_UDR_1 = split_res_LR_12872[1]
lineage_GDS_1.end_at_lineage(lineage_L'A_1, 12881.1, 12905.1)
lineage_FTSF_1.terminate_at(6170.849999999999)
lineage_PSR_1.terminate_at(6133.8)
lineage_POF_1.terminate_at(6133.8)
lineage_CCSR_1.terminate_at(5883.15)
lineage_POSR_1.terminate_at(6343.05)
lineage_ACR_1.terminate_at(5924.25)
lineage_FGSRI_1.terminate_at(6139.2)
lineage_FSRI_1.terminate_at(6139.2)
lineage_PSdF_1.terminate_at(6343.05)
lineage_FSR_1.terminate_at(6170.849999999999)
lineage_PSF_1.terminate_at(6343.05)
lineage_SFIO_4.terminate_at(9864.6)
lineage_PRS-1907_2.terminate_at(6873.75)
lineage_PO-1914_1.terminate_at(7029.0)
lineage_PRS-1914_1.terminate_at(6873.75)
lineage_PSN_1.terminate_at(7202.55)
lineage_PSF-1920_1.terminate_at(7498.799999999999)
lineage_UFS_1.terminate_at(7329.9)
lineage_PCU_1.terminate_at(7329.9)
lineage_PRS-1923_1.terminate_at(7498.799999999999)
lineage_PSC_1.terminate_at(7748.7)
lineage_PSF-1929_1.terminate_at(8015.4)
lineage_PAPF_1.terminate_at(8527.949999999999)
lineage_PRS-1928_1.terminate_at(8015.4)
lineage_POP_1.terminate_at(7748.7)
lineage_GBL_1.terminate_at(8039.549999999999)
lineage_PUP_1.terminate_at(8083.65)
lineage_PSdF-UJJ_1.terminate_at(8015.4)
lineage_JSR_1.terminate_at(8039.549999999999)
lineage_USR_1.terminate_at(8272.05)
lineage_PRAS_1.terminate_at(8243.4)
lineage_POI_1.terminate_at(8471.55)
lineage_CCI_1.terminate_at(8471.55)
lineage_PSOP_1.terminate_at(8243.4)
lineage_GO_1.terminate_at(8471.55)
lineage_PPUS_1.terminate_at(8852.85)
lineage_CIR_1.terminate_at(9966.3)
lineage_UCRG_1.terminate_at(9864.6)
lineage_UGCS_1.terminate_at(9864.6)
lineage_PRG-1971_1.terminate_at(12513.449999999999)
lineage_MÉP_1.terminate_at(10658.25)
lineage_RPF_1.terminate_at(11657.1)
lineage_CÉ_1.terminate_at(10658.25)
lineage_NUDF_1.terminate_at(11933.55)
lineage_GDS_1.terminate_at(12905.1)
lineage_CSDR_1.join(12777.6, 12801.6, bundle_CONV_FED, 0)
lineage_FP_1.join(12899.1, 12923.1, bundle_CONV_FED, 1)
lineage_PRG-2019_1.join(12771.449999999999, 12795.449999999999, bundle_CONV_FED, 1)
lineage_EC_1.join(12889.949999999999, 12913.949999999999, bundle_CONV_FED, 1)
lineage_RI_1.join(10306.05, 10330.05, bundle_UDF, 0)
lineage_G·s_1.join(12646.35, 12670.35, var_3, -1)
lineage_PRAD_2.join(11645.1, 11669.1, var_4, 1)
lineage_PRAD_2.leave(12141.3, 12165.3, var_4, 367.5)
lineage_TdP_1.join(12762.9, 12786.9, var_5, 1)
lineage_Agir_1.join(12762.9, 12786.9, var_5, -1)
diagram.generate('political_diagram.svg')