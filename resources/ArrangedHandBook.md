# Zygo MX Python API 完整技術文檔

## 目錄
- [系統需求與環境](#系統需求與環境)
- [一、核心功能模塊](#一核心功能模塊)
  - [連接管理](#連接管理)
  - [應用程序控制](#應用程序控制)
  - [數據操作](#數據操作)
  - [運動控制](#運動控制)
  - [測量與分析](#測量與分析)
- [二、基礎功能模塊](#二基礎功能模塊)
  - [單位系統](#單位系統)
  - [系統命令](#系統命令)
  - [結果和控制](#結果和控制)
  - [設置操作](#設置操作)
- [三、進階功能模塊](#三進階功能模塊)
  - [切片管理](#切片管理)
  - [MST測量功能](#mst測量功能)
  - [基準點管理](#基準點管理)
  - [QDAS統計分析](#qdas統計分析)
- [四、輔助功能模塊](#四輔助功能模塊)
  - [圖表控制](#圖表控制)
  - [掩模管理](#掩模管理)
  - [圖案管理](#圖案管理)
  - [日誌記錄](#日誌記錄)
  - [注釋管理](#注釋管理)
- [五、最佳實踐與注意事項](#五最佳實踐與注意事項)

## 系統需求與環境

- Python 3.4.3
- Windows 10 Enterprise 2016 LTSB
- Zygo MX 軟件
- 硬件配置：
  - CPU: Intel64 Family 6 Model 158 Stepping 9
  - 記憶體: 32,632 MB
  - 系統類型: x64-based PC

## 一、核心功能模塊

### 連接管理

核心類別：
```python
class WebServiceState(IntEnum):
    none = 0    # 無狀態
    idle = 1    # 空閒
    active = 2  # 活動
```

核心功能：
```python
def connect(force_if_active=False, host='localhost', port=8733, uid=''):
    """建立與MX的連接
    Parameters:
        force_if_active (bool): 是否強制連接
        host (str): 主機名或IP
        port (int): 端口號
        uid (str): 連接ID
    Returns:
        str: 連接的唯一標識符
    """

def terminate():
    """關閉與MX的連接"""

def get_service_state():
    """獲取當前服務狀態"""

def get_uid():
    """獲取當前連接ID"""

def get_is_remote_access_connected():
    """檢查遠程訪問狀態"""
```

HTTP請求處理：
```python
def send_request(service, method, params=None, *, decode=True):
    """發送HTTP請求
    Parameters:
        service (str): 服務名稱
        method (str): 方法名稱
        params (dict): 參數字典
        decode (bool): 是否解碼JSON
    """

def get_send_request(service, method, params=None, *, decode=True):
    """發送HTTP請求並獲取返回值"""
```

### 應用程序控制

核心方法：
```python
def is_application_open():
    """檢查MX應用程序是否開啟
    Returns: bool"""

def get_application_path():
    """獲取應用程序路徑
    Returns: str or None"""

def open_application(filename):
    """打開MX應用程序
    Parameters:
        filename (str): 應用程序路徑"""

def close_application():
    """關閉當前應用程序"""

def save_application_as(filename):
    """保存應用程序
    Parameters:
        filename (str): 保存路徑"""
```

### 數據操作

基本操作：
```python
def analyze():
    """分析當前數據"""

def load_data(filename):
    """加載數據文件
    Parameters:
        filename (str): 數據文件路徑"""

def save_data(filename):
    """保存數據
    Parameters:
        filename (str): 保存路徑"""
```

高級數據操作：
```python
def subtract_data(filename, ignore_lateral_res=True, use_input_size=False, 
                 use_system_size=False, use_fiducial_alignment=False,
                 alignment_type=FiducialAlignmentType.fixed,
                 alignment_tolerance=1.0):
    """數據減法操作"""

def scale_data(scale_value):
    """數據縮放
    Parameters:
        scale_value (float): 縮放因子"""
```

### 運動控制

軸類型定義：
```python
class AxisType(IntEnum):
    """軸名稱定義"""
    unknown = 0  # 未知軸
    x = 1        # X軸
    y = 2        # Y軸
    z = 3        # Z軸
    rx = 4       # Pitch軸
    ry = 5       # Roll軸
    rz = 6       # Theta軸
    x2 = 7       # 第二X軸
    y2 = 8       # 第二Y軸
    z2 = 9       # 第二Z軸
    rx2 = 10     # 第二Pitch軸
    ry2 = 11     # 第二Roll軸
    rz2 = 12     # 第二Theta軸

class StageType(IntEnum):
    """平台類型定義"""
    stage_all = 0  # 所有平台
    stage1 = 1     # 平台1
    stage2 = 2     # 平台2
```

位置控制：
```python
# 基本軸位置獲取
def get_x_pos(unit, stage=StageType.stage1):
    """獲取X軸位置"""
def get_y_pos(unit, stage=StageType.stage1):
    """獲取Y軸位置"""
def get_z_pos(unit, stage=StageType.stage1):
    """獲取Z軸位置"""

# 角度軸位置獲取
def get_p_pos(unit, stage=StageType.stage1):
    """獲取Pitch軸位置"""
def get_r_pos(unit, stage=StageType.stage1):
    """獲取Roll軸位置"""
def get_t_pos(unit, stage=StageType.stage1):
    """獲取Theta軸位置"""
```

運動命令：
```python
# 單軸運動
def move_x(x_pos, unit, wait=True, stage=StageType.stage1):
    """移動X軸"""
def move_y(y_pos, unit, wait=True, stage=StageType.stage1):
    """移動Y軸"""
def move_z(z_pos, unit, wait=True, stage=StageType.stage1):
    """移動Z軸"""

# 多軸聯動
def move_xy(x_pos, y_pos, unit, wait=True, stage=StageType.stage1):
    """同時移動XY軸"""
def move_xyz(x_pos, y_pos, z_pos, unit, wait=True, stage=StageType.stage1):
    """同時移動XYZ軸"""
```

回原點操作：
```python
def home_x(wait=True, stage=StageType.stage1):
    """X軸回原點"""
def home_y(wait=True, stage=StageType.stage1):
    """Y軸回原點"""
def home_z(wait=True, stage=StageType.stage1):
    """Z軸回原點"""
def home_xyz(wait=True, stage=StageType.stage1):
    """XYZ軸同時回原點"""
def home_all(wait=True, stage=StageType.stage_all):
    """所有軸回原點"""
```

### 測量與分析

數據採集：
```python
def acquire(wait=True):
    """獲取數據
    Parameters:
        wait (bool): 是否等待完成
    Returns:
        AcquisitionTask: 採集任務對象"""

def measure(wait=True):
    """測量數據（acquire + analyze）"""
```

自動優化：
```python
def auto_focus():
    """自動對焦"""
def auto_tilt():
    """自動傾斜調整"""
def auto_focus_tilt():
    """自動對焦和傾斜調整"""
def auto_light_level():
    """自動光照水平調整"""
def auto_lat_cal(value, unit):
    """自動橫向校準"""
```

硬件控制：
```python
# 轉台控制
def get_turret():
    """獲取轉台位置"""
def move_turret(position):
    """移動轉台"""

# 變焦控制
def get_zoom():
    """獲取變焦值"""
def set_zoom(zoom):
    """設置變焦"""
def lock_zoom():
    """鎖定變焦"""
def unlock_zoom():
    """解鎖變焦"""

# 光照控制
def get_light_level():
    """獲取光照水平"""
def set_light_level(light_level):
    """設置光照水平"""
```

## 二、基礎功能模塊

### 單位系統

測量單位定義：
```python
class Units(IntEnum):
    # 線性測量單位
    Angstroms = 1
    MicroMeters = 2
    MilliMeters = 3
    Meters = 4
    Inches = 5
    MicroInches = 6
    Mils = 7
    NanoMeters = 8

    # 角度單位
    Degrees = 20
    ArcMinutes = 21
    ArcSeconds = 22
    Radians = 23
    MicroRadians = 24
    MilliRadians = 25

    # 面積單位
    SquareMicroMeters = 40
    SquareMilliMeters = 41
    SquareMeters = 42
    SquareInches = 43

    # 體積單位
    CubicMicroMeters = 60
    CubicMilliMeters = 61
    CubicMeters = 62
    CubicInches = 63

    # 特殊單位
    Waves = 80
    UserWaves = 81
    Fringes = 82
    FringeRadians = 83
    Pixels = 84
    Invalid = 0
    NotSet = -1
    NoUnits = -2
    Scaled = -3
```

### 系統命令

文件類型：
```python
class FileTypes(Enum):
    All = ()
    UI_Application = ()
    Script = ()
    Csv = ()
    Data = ()
    Signal_Data = ()
    Setting = ()
    Image = ()
    Recipe = ()
    Result = ()
    Mask = ()
```

目錄操作：
```python
def get_bin_dir():
    """獲取可執行文件目錄"""

def get_working_dir():
    """獲取工作目錄"""

def get_open_dir(file_type):
    """獲取打開目錄"""

def get_save_dir(file_type):
    """獲取保存目錄"""

def set_open_dir(file_type, path):
    """設置打開目錄"""

def set_save_dir(file_type, path):
    """設置保存目錄"""
```

文件操作：
```python
def list_files_in_open_dir(file_type):
    """列出打開目錄中的文件"""

def list_files_in_dir(directory, extensions, recursive=False):
    """列出指定目錄中的文件"""
```

### 結果和控制

獲取值：
```python
def get_result_number(path, unit=None):
    """獲取數值結果"""

def get_control_string(path):
    """獲取控制字符串"""

def get_result_bool(path):
    """獲取布爾結果"""
```

設置值：
```python
def set_result_number(path, value, unit=None):
    """設置數值結果"""

def set_control_string(path, value):
    """設置控制字符串"""

def set_result_bool(path, value):
    """設置布爾結果"""
```

### 設置操作

```python
def load_settings(filename):
    """加載設置文件"""

def save_settings(filename):
    """保存設置"""

def load_settings_using_options(filename, options):
    """使用選項加載設置"""
```

## 三、進階功能模塊

### 切片管理

切片類型：
```python
class LinearSliceType(IntEnum):
    """線性切片類型"""
    linear = 1

class RadialSliceType(IntEnum):
    """徑向切片類型"""
    radial = 1
    radial_center = 2
    average_radial = 3
    average_radial_center = 4

class CircularSliceType(IntEnum):
    """圓形切片類型"""
    circular = 1
    circular_center = 2
    circular_min_pv = 3
```

基礎切片類：
```python
class Slice:
    @property
    def label(self):
        """獲取切片標籤"""
        
    def get_dimension(self, units):
        """獲取切片尺寸"""
        
    def set_dimension(self, value, units):
        """設置切片尺寸"""
        
    def get_midpoint(self, units):
        """獲取中點坐標"""
        
    def set_midpoint(self, position, units):
        """設置中點坐標"""
        
    def get_angle(self, units):
        """獲取切片角度"""
        
    def set_angle(self, value, units):
        """設置切片角度"""

class LinearSlice(Slice):
    """線性切片"""
    
    def get_endpoints(self, units):
        """獲取起點和終點坐標"""
        
    def get_start(self, units):
        """獲取起點坐標"""
        
    def set_start(self, position, units):
        """設置起點坐標"""
        
    def get_end(self, units):
        """獲取終點坐標"""
        
    def set_end(self, position, units):
        """設置終點坐標"""
        
    def get_length(self, units):
        """獲取切片長度"""
        
    def set_length(self, value, units):
        """設置切片長度"""

class RadialSlice(Slice):
    """徑向切片"""
    
    def get_length(self, units):
        """獲取切片長度"""
        
    def set_length(self, value, units):
        """設置切片長度"""
        
    def get_endpoints(self, units):
        """獲取切片端點"""
        
    def get_start(self, units):
        """獲取起點"""
        
    def set_start(self, position, units):
        """設置起點"""

class CircularSlice(Slice):
    """圓形切片"""
    
    def get_radius(self, units):
        """獲取半徑"""
        
    def set_radius(self, value, units):
        """設置半徑"""
        
    def get_center(self, units):
        """獲取圓心"""
        
    def set_center(self, position, units):
        """設置圓心"""

# 切片獲取函數
def get_linear_slices(control, linear_slice_type):
    """獲取線性切片"""
    
def get_all_linear_slices(control):
    """獲取所有線性切片"""
    
def get_radial_slices(control, radial_slice_type):
    """獲取徑向切片"""
    
def get_all_radial_slices(control):
    """獲取所有徑向切片"""
    
def get_circular_slices(control, circular_slice_type):
    """獲取圓形切片"""
    
def get_all_circular_slices(control):
    """獲取所有圓形切片"""

### MST測量功能

峰值分析：
```python
def get_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit):
    """獲取指定峰值位置
    Parameters:
        peak_num (int): 峰值序號
        num_peaks (int): 預期峰值數量
        range_min (float): 最小光程差
        range_max (float): 最大光程差
        unit (Units): 單位
    Returns:
        float: 峰值光程差"""

def get_averaged_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit, averages):
    """獲取多點平均峰值位置
    Parameters:
        averages (int): 採樣點數"""

def analyze_ftpsi_peak(peak_location, unit):
    """在指定光程差位置執行MST分析"""
```

掃描參數：
```python
def get_min_excursion(unit):
    """獲取最小掃描振幅"""
    
def get_max_excursion(unit):
    """獲取最大掃描振幅"""
    
def get_min_rate(unit):
    """獲取最小掃描速率"""
    
def get_max_rate(unit):
    """獲取最大掃描速率"""
    
def get_min_frames():
    """獲取最小幀數"""
    
def get_max_frames():
    """獲取最大幀數"""
```

測試點控制：
```python
def get_test_x():
    """獲取測試點X坐標"""
    
def get_test_y():
    """獲取測試點Y坐標"""
    
def get_reference_x():
    """獲取參考點X坐標"""
    
def get_reference_y():
    """獲取參考點Y坐標"""
    
def set_test(x, y):
    """設置測試點"""
    
def set_reference(x, y):
    """設置參考點"""
    
def clear_test():
    """清除測試點"""
    
def clear_reference():
    """清除參考點"""
```

掃描參數估算：
```python
def estimate_ramp_excursion(maximum_opd_gap, tuning_factor, opd_units, 
                          minimum_opd_gap=0, result_units=Units.GigaHertz):
    """估算掃描振幅"""
    
def estimate_ramp_frames(maximum_opd_gap, tuning_factor, opd_units, 
                        minimum_opd_gap=0):
    """估算掃描幀數"""
```

### 基準點管理

基準點類：
```python
class Fiducial:
    """基準點"""
    
    @property
    def center(self):
        """獲取中心坐標"""
        
    @property
    def height(self):
        """獲取高度"""
        
    @property
    def width(self):
        """獲取寬度"""
        
    def move_absolute(self, x, y):
        """移動到絕對位置"""
            
    def move_relative(self, x, y):
        """相對移動"""
            
    def resize(self, height, width):
        """調整尺寸"""
            
    def rotate(self, value, unit):
        """旋轉"""
```

基準點集合：
```python
class Fiducials:
    """基準點集合"""
    
    def get_num_sets(self):
        """獲取工作集數量"""
        
    def get_num_fiducials(self, working_set=None):
        """獲取基準點數量"""
            
    def save(self, filename):
        """保存基準點"""
        
    def load(self, filename):
        """加載基準點"""
        
    def delete(self, fiducial):
        """刪除基準點"""
        
    def clear_set(self, working_set):
        """清空工作集"""
        
    def delete_set(self, working_set):
        """刪除工作集"""
        
    def add_set(self):
        """新建工作集"""
        
    def get_fiducial_closest_to(self, x, y, working_set=None):
        """獲取最近基準點"""
```

### QDAS統計分析

研究類型：
```python
class QdasStudyType(IntEnum):
    """QDAS研究類型"""
    standard = 0    # 標準生產
    type_1 = 1     # Type 1研究
    type_2 = 2     # Type 2研究
    type_3 = 3     # Type 3研究

class OperationPromptType(IntEnum):
    """操作提示類型"""
    none = 0           # 無提示
    info = 1           # 信息提示
    serial = 2         # 序列號提示
    unique_serial = 3  # 唯一序列號提示
```

測試計劃操作：
```python
def create_qdas_testplan(testplan_path=None, qdas_params_path=None, 
                        auto_kfields=None):
    """創建測試計劃"""
    
def export_qdas_results(testplan_path=None, qdas_results_path=None,
                       auto_kfields=None, study_type=QdasStudyType.standard,
                       silent=False):
    """導出結果"""
```

研究執行：
```python
def do_standard(spc_testplan, testplan_info, operation, auto_kfields=None):
    """執行標準研究"""
    
def do_type_1(spc_testplan, testplan_info, operation, auto_kfields=None,
              prompt=OperationPromptType.info, sequence_start=None):
    """執行Type 1研究"""
    
def do_type_2(spc_testplan, testplan_info, operation, auto_kfields=None,
              prompt=OperationPromptType.info, sequence_start=None):
    """執行Type 2研究"""
```

特徵值類：
```python
class QdasCharacteristic:
    """QDAS特徵值"""
    
    @property
    def uid(self):
        """獲取ID"""
        
    @property
    def name(self):
        """獲取名稱"""
        
    @property
    def groupname(self):
        """獲取分組"""
        
    @property
    def unit(self):
        """獲取單位"""
        
    @property
    def nominal(self):
        """獲取標稱值"""
        
    @property
    def ltol(self):
        """獲取下限"""
        
    @property
    def utol(self):
        """獲取上限"""
```

## 四、輔助功能模塊

### 圖表控制

圖表類型：
```python
class ChartAxis(IntEnum):
    """圖表軸"""
    X = 1      # X軸
    Y = 2      # Y軸
    All = 3    # 所有軸

class ChartLimit(IntEnum):
    """限制值類型"""
    Low = 1    # 下限
    High = 2   # 上限
    All = 3    # 所有限制
```

限制值操作：
```python
def clear_chart_limit(control, axis_name=ChartAxis.All,
                     limit_name=ChartLimit.All):
    """清除限制值"""
    
def set_chart_high_limit(control, axis_name=ChartAxis.Y,
                        limit_value=0, unit=Units.MicroMeters):
    """設置上限"""
    
def set_chart_low_limit(control, axis_name=ChartAxis.Y,
                       limit_value=0, unit=Units.MicroMeters):
    """設置下限"""
    
def set_chart_limits(control, axis_name=ChartAxis.Y,
                    low_value=0, high_value=100, unit=Units.MicroMeters):
    """同時設置上下限"""
```

### 掩模管理

掩模類：
```python
class Mask:
    """掩模"""
    
    @property
    def center(self):
        """獲取中心"""
        
    @property
    def height(self):
        """獲取高度"""
        
    @property
    def width(self):
        """獲取寬度"""
        
    @property
    def type(self):
        """獲取類型"""
        
    def move_absolute(self, x, y):
        """移動到絕對位置"""
            
    def move_relative(self, x, y):
        """相對移動"""
            
    def resize(self, height, width):
        """調整尺寸"""
            
    def rotate(self, value, unit):
        """旋轉"""
```

掩模集合：
```python
class Masks:
    """掩模集合"""
    
    def get_num_masks(self, mask_type=None):
        """獲取掩模數量"""
            
    def save(self, filename):
        """保存掩模"""
        
    def load(self, filename):
        """加載掩模"""
        
    def delete(self, mask):
        """刪除掩模"""
        
    def clear(self, mask_type=None):
        """清除掩模"""
        
    def get_mask_closest_to(self, x, y, mask_type=None):
        """獲取最近掩模"""
```

### 圖案管理

基本操作：
```python
def save(filename):
    """保存圖案"""
    
def load(filename):
    """加載圖案"""
    
def run():
    """執行圖案"""
```

拼接操作：
```python
def load_stitch(filename):
    """加載拼接設置"""
    
def load_and_stitch(folder):
    """加載並執行拼接"""
```

對齊操作：
```python
def prealign():
    """預對齊"""
    
def align():
    """最終對齊"""
```

### 日誌記錄

```python
def log_trace(message):
    """跟蹤日誌"""
    
def log_debug(message):
    """調試日誌"""
    
def log_info(message):
    """信息日誌"""
    
def log_warn(message):
    """警告日誌"""
    
def log_error(message):
    """錯誤日誌"""
    
def log_fatal(message):
    """致命錯誤日誌"""
```

### 注釋管理

```python
def create_annotation(name, value):
    """創建注釋"""
    
def get_annotation(path):
    """獲取注釋"""
    
def set_annotation(path, value):
    """設置注釋"""
    
def delete_annotation(path):
    """刪除注釋"""
```

## 五、最佳實踐與注意事項

1. 錯誤處理
```python
try:
    # 執行操作
    connect()
    open_application()
except ZygoError as e:
    log_error(f"操作失敗: {str(e)}")
finally:
    terminate()
```

2. 資源管理
- 使用 try-finally 確保資源釋放
- 及時關閉連接
- 正確處理文件操作

3. 性能優化
- 批量處理時使用異步操作
- 合理設置等待超時
- 避免不必要的數據轉換

4. 代碼規範
- 使用恰當的異常處理
- 保持代碼結構清晰
- 添加必要的註釋和文檔
- 使用有意義的變量命名
- 避免重複代碼

5. 測量流程建議
- 測量前進行必要的校準
- 確保環境穩定性
- 正確設置測量參數
- 保存原始數據
- 定期備份重要數據

6. 具體實現範例

### 基本測量流程
```python
from zygo.mx import connect, terminate
from zygo.application import open_application
from zygo.motion import home_all
from zygo.units import Units

try:
    # 建立連接
    uid = connect(host='localhost', port=8733)
    print(f"Connected with UID: {uid}")
    
    # 打開應用
    open_application("D:/MX/Applications/standard_measure.mx")
    
    # 回原點
    home_all(wait=True)
    
    # 載入設置
    load_settings("D:/MX/Settings/measure_settings.xml")
    
    # 自動優化
    auto_focus()
    auto_tilt()
    auto_light_level()
    
    # 執行測量
    measure(wait=True)
    
    # 保存數據
    save_data("D:/MX/Data/measurement_result.dat")
    
except ZygoError as e:
    log_error(f"Measurement failed: {str(e)}")
finally:
    terminate()
```

### QDAS數據收集
```python
from zygo.qdas import create_qdas_testplan, do_standard
from zygo.mx import measure

def measurement_operation():
    """單次測量操作"""
    # 執行測量
    measure(wait=True)
    
    # 獲取結果
    result = get_result_number(("Results", "PV"), unit=Units.MicroMeters)
    return result

try:
    # 創建測試計劃
    testplan = create_qdas_testplan(
        testplan_path="D:/QDAS/testplan.TestPlan",
        qdas_params_path="D:/QDAS/params.csv",
        auto_kfields=["K1001", "K2001"]
    )
    
    # 執行標準研究
    do_standard(
        spc_testplan=testplan,
        testplan_info={"part_number": "TEST001"},
        operation=measurement_operation,
        auto_kfields={"K1001": "BATCH001"}
    )
    
except Exception as e:
    log_error(f"QDAS collection failed: {str(e)}")
```

### 自動化數據處理
```python
from zygo.mx import load_data, analyze, save_data
import os

def process_data_files(input_dir, output_dir):
    """批量處理數據文件"""
    try:
        # 獲取所有.dat文件
        data_files = [f for f in os.listdir(input_dir) 
                     if f.endswith('.dat')]
        
        for file in data_files:
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, f"processed_{file}")
            
            # 載入數據
            load_data(input_path)
            
            # 處理數據
            analyze()
            scale_data(1.5)
            
            # 保存結果
            save_data(output_path)
            
            log_info(f"Processed {file}")
            
    except Exception as e:
        log_error(f"Data processing failed: {str(e)}")
```

### 切片分析
```python
from zygo.slices import (get_all_linear_slices, LinearSliceType,
                        get_circular_slices, CircularSliceType)
from zygo.units import Units

def analyze_slices(plot_control):
    """分析切片數據"""
    results = {}
    
    # 分析線性切片
    linear_slices = get_all_linear_slices(plot_control)
    for label, slice in linear_slices.items():
        length = slice.get_length(Units.MicroMeters)
        results[f"Linear_{label}"] = length
        
    # 分析圓形切片
    circular_slices = get_circular_slices(
        plot_control, 
        CircularSliceType.circular
    )
    for slice in circular_slices:
        radius = slice.get_radius(Units.MicroMeters)
        center = slice.get_center(Units.MicroMeters)
        results[f"Circular_{slice.label}"] = {
            "radius": radius,
            "center_x": center.x,
            "center_y": center.y
        }
        
    return results
```

7. 環境配置建議

Windows系統配置：
- 啟用長路徑支持
- 設置適當的系統環境變量
- 確保Python 3.4.3版本

Python環境配置：
- 創建獨立的虛擬環境
- 安裝必要的依賴包
- 配置正確的PYTHONPATH

網絡配置：
- 確保防火牆允許需要的端口
- 配置正確的IP地址
- 測試網絡連通性

8. 故障排除指南

連接問題：
- 檢查網絡設置
- 驗證主機名和端口
- 確認服務狀態
- 檢查防火牆設置

測量問題：
- 校準儀器
- 檢查環境條件
- 驗證參數設置
- 檢查硬件狀態

數據問題：
- 驗證文件格式
- 檢查存儲空間
- 備份重要數據
- 驗證數據完整性

9. 安全性考慮

數據安全：
- 定期備份數據
- 使用安全的存儲位置
- 實施訪問控制
- 加密敏感數據

操作安全：
- 使用try-except處理異常
- 實施錯誤恢復機制
- 記錄重要操作
- 定期維護系統

網絡安全：
- 使用安全的網絡協議
- 限制網絡訪問
- 監控網絡活動
- 更新安全補丁