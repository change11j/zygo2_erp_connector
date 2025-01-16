### 12. 基準點管理 (Fiducials Management)

基準點管理模組提供了對MX基準點(Fiducial)的完整操作功能。

#### 基準點類 (Fiducial Class)

```python
class Fiducial:
    """代表單個MX基準點"""
    
    @property
    def center(self):
        """獲取基準點中心坐標(Point2D對象)"""
        
    @property
    def height(self):
        """獲取基準點高度"""
        
    @property
    def width(self):
        """獲取基準點寬度"""
        
    def move_absolute(self, x, y):
        """移動基準### 10. 切片管理 (Slices Management)

切片管理模組提供了對MX中各種切片(線性、徑向、圓形)的完整操作功能。

#### 切片類型定義

```python
class LinearSliceType(IntEnum):
    """線性切片類型"""
    linear = 1  # 標準線性切片

class RadialSliceType(IntEnum):
    """徑向切片類型"""
    radial = 1                  # 標準徑向切片
    radial_center = 2           # 中心徑向切片
    average_radial = 3          # 平均徑向切片
    average_radial_center = 4   # 中心平均徑向切片

class CircularSliceType(IntEnum):
    """圓形切片類型"""
    circular = 1        # 標準圓形切片
    circular_center = 2 # 中心圓形切片
    circular_min_pv = 3 # 最小PV圓形切片
```

#### 切片基類 (Slice)

```python
class Slice:
    """MX切片基類"""
    
    @property
    def label(self):
        """獲取切片標籤"""
        
    def get_dimension(self, units):
        """獲取切片尺寸
        
        根據切片類型返回不同含義:
        - 線性切片: 切片長度
        - 圓形切片: 切片半徑
        - 徑向切片: 切片長度或半徑(取決於子類型)"""
        
    def set_dimension(self, value, units):
        """設置切片尺寸"""
        
    def get_midpoint(self, units):
        """獲取切片中點坐標"""
        
    def set_midpoint(self, position, units):
        """設置切片中點坐標"""
        
    def get_angle(self, units):
        """獲取切片角度"""
        
    def set_angle(self, value, units):
        """設置切片角度"""
```

#### 線性切片 (LinearSlice)

```python
class LinearSlice(Slice):
    """MX線性切片"""
    
    def get_endpoints(self, units):
        """獲取切片起點和終點坐標
        Returns: (Point2D, Point2D)元組"""
        
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
```

#### 徑向切片 (RadialSlice)

```python
class RadialSlice(Slice):
    """MX徑向切片"""
    
    def get_length(self, units):
        """獲取切片長度"""
        
    def set_length(self, value, units):
        """設置切片長度"""
        
    def get_endpoints(self, units):
        """獲取切片起點和終點坐標"""
        
    def get_start(self, units):
        """獲取起點坐標"""
        
    def set_start(self, position, units):
        """設置起點坐標"""
```

#### 圓形切片 (CircularSlice)

```python
class CircularSlice(Slice):
    """MX圓形切片"""
    
    def get_radius(self, units):
        """獲取切片半徑"""
        
    def set_radius(self, value, units):
        """設置切片半徑"""
        
    def get_center(self, units):
        """獲取圓心坐標"""
        
    def set_center(self, position, units):
        """設置圓心坐標"""
```

#### 切片獲取函數

**線性切片:**
```python
def get_linear_slices(control, linear_slice_type):
    """獲取指定類型的線性切片
    
    Parameters:
        control (Control): 圖表控件
        linear_slice_type (LinearSliceType): 切片類型
    Returns:
        tuple of LinearSlice: 切片列表"""
        
def get_all_linear_slices(control):
    """獲取所有線性切片
    Returns: dict[str, LinearSlice]"""
```

**徑向切片:**
```python
def get_radial_slices(control, radial_slice_type):
    """獲取指定類型的徑向切片"""
    
def get_all_radial_slices(control):
    """獲取所有徑向切片"""
```

**圓形切片:**
```python
def get_circular_slices(control, circular_slice_type):
    """獲取指定類型的圓形切片"""
    
def get_all_circular_slices(control):
    """獲取所有圓形切片"""
```

#### 使用範例

```python
from zygo.slices import (get_all_linear_slices, LinearSliceType,
                        get_circular_slices, CircularSliceType)
from zygo.units import Units

# 獲取所有線性切片
linear_slices = get_all_linear_slices(plot_control)
for label, slice in linear_slices.items():
    # 獲取切片長度
    length = slice.get_length(Units.MicroMeters)
    print(f"Linear slice {label}: length = {length}μm")
    
# 獲取標準圓形切片
circular_slices = get_circular_slices(plot_control, CircularSliceType.circular)
for slice in circular_slices:
    # 獲取半徑
    radius = slice.get_radius(Units.MicroMeters)
    # 獲取圓心
    center = slice.get_center(Units.MicroMeters)
    print(f"Circular slice {slice.label}:")
    print(f"  radius = {radius}μm")
    print(f"  center = ({center.x}, {center.y})μm")
```

### 11. MST測量功能 (MST Measurement)

MST(Measure-Subtract-Test)模組提供了對FTPSI(Frequency Transform Phase Shifting Interferometry)測量功能的支持。

#### 峰值分析

**get_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit)**
- 功能：根據OPD光譜計算獲取指定峰值位置
- 參數：
  - peak_num (int): 峰值序號
  - num_peaks (int): 預期峰值數量
  - range_min (float): 光程差最小值
  - range_max (float): 光程差最大值
  - unit (Units): 單位
- 返回：float (指定峰值的光程差)

**get_averaged_ftpsi_peak(peak_num, num_peaks, range_min, range_max, unit, averages)**
- 功能：獲取多點平均的峰值位置
- 額外參數：
  - averages (int): 採樣點數

**analyze_ftpsi_peak(peak_location, unit)**
- 功能：在指定光程差位置執行MST分析生成相位圖
- 參數：
  - peak_location (float): 峰值光程差
  - unit (Units): 單位

#### 掃描參數獲取

**振幅範圍:**
```python
def get_min_excursion(unit):
    """獲取FTPSI最小掃描振幅"""
    
def get_max_excursion(unit):
    """獲取FTPSI最大掃描振幅"""
```

**掃描速率:**
```python
def get_min_rate(unit):
    """獲取FTPSI最小掃描速率"""
    
def get_max_rate(unit):
    """獲取FTPSI最大掃描速率"""
```

**幀數範圍:**
```python
def get_min_frames():
    """獲取FTPSI最小幀數"""
    
def get_max_frames():
    """獲取FTPSI最大幀數"""
```

#### 測試和參考點控制

**坐標獲取:**
```python
def get_test_x():
    """獲取測試點X坐標(像素)"""
    
def get_test_y():
    """獲取測試點Y坐標(像素)"""
    
def get_reference_x():
    """獲取參考點X坐標(像素)"""
    
def get_reference_y():
    """獲取參考點Y坐標(像素)"""
```

**坐標設置:**
```python
def set_test(x, y):
    """設置測試點位置"""
    
def set_reference(x, y):
    """設置參考點位置"""
    
def clear_test():
    """清除測試點"""
    
def clear_reference():
    """清除參考點"""
```

#### 掃描參數估算

**estimate_ramp_excursion(maximum_opd_gap, tuning_factor, opd_units, minimum_opd_gap=0, result_units=Units.GigaHertz)**
- 功能：估算多表面測量的FTPSI掃描振幅
- 參數：
  - maximum_opd_gap (float): 最大OPD間隔
  - tuning_factor (int): 調諧因子
  - opd_units (Units): OPD單位
  - minimum_opd_gap (float): 最小OPD間隔
  - result_units (Units): 結果單位
- 返回：預估掃描振幅

**estimate_ramp_frames(maximum_opd_gap, tuning_factor, opd_units, minimum_opd_gap=0)**
- 功能：估算多表面測量所需的FTPSI掃描幀數
- 返回：預估幀數

#### 使用範例

1. 峰值分析:
```python
from zygo.mst import get_ftpsi_peak, analyze_ftpsi_peak
from zygo.units import Units

# 獲取峰值位置
peak = get_ftpsi_peak(
    peak_num=1,
    num_peaks=2,
    range_min=0,
    range_max=1000,
    unit=Units.MicroMeters
)

# 執行MST分析
analyze_ftpsi_peak(peak, Units.MicroMeters)
```

2. 掃描參數設置:
```python
from zygo.mst import set_test, set_reference

# 設置測試點和參考點
set_test(100, 100)
set_reference(200, 200)

# 清除設置
clear_test()
clear_reference()
```

3. 掃描參數估算:
```python
from zygo.mst import estimate_ramp_excursion, estimate_ramp_frames

# 估算掃描振幅
excursion = estimate_ramp_excursion(
    maximum_opd_gap=500,
    tuning_factor=2,
    opd_units=Units.MicroMeters
)

# 估算掃描幀數
frames = estimate_ramp_frames(
    maximum_opd_gap=500,
    tuning_factor=2,
    opd_units=Units.MicroMeters
)
```

### 12. 基準點管理 (Fiducials Management)

基準點管理模組提供了對MX基準點(Fiducial)的完整操作功能。

#### 基準點類 (Fiducial Class)

```python
class Fiducial:
    """代表單個MX基準點"""
    
    @property
    def center(self):
        """獲取基準點中心坐標(Point2D對象)"""
        
    @property
    def height(self):
        """獲取基準點高度"""
        
    @property
    def width(self):
        """獲取基準點寬度"""
        
    def move_absolute(self, x, y):
        """移動基準點中心到指定絕對位置
        
        Parameters:
            x (float): 新的X坐標
            y (float): 新的Y坐標"""
            
    def move_relative(self, x, y):
        """按相對距離移動基準點中心
        
        Parameters:
            x (float): X方向移動距離
            y (float): Y方向移動距離"""
            
    def resize(self, height, width):
        """調整基準點尺寸
        
        Parameters:
            height (float): 新的高度
            width (float): 新的寬度"""
            
    def rotate(self, value, unit):
        """旋轉基準點
        
        Parameters:
            value (float): 旋轉角度
            unit (Units): 角度單位"""
```

#### 基準點集合類 (Fiducials Class)

```python
class Fiducials:
    """代表MX基準點集合"""
    
    def get_num_sets(self):
        """獲取工作集數量"""
        
    def get_num_fiducials(self, working_set=None):
        """獲取指定工作集中的基準點數量
        
        Parameters:
            working_set (int): 工作集索引,None表示所有工作集"""
            
    def save(self, filename):
        """保存基準點到文件"""
        
    def load(self, filename):
        """從文件載入基準點"""
        
    def delete(self, fiducial):
        """刪除指定基準點"""
        
    def clear_set(self, working_set):
        """清空指定工作集"""
        
    def delete_set(self, working_set):
        """刪除指定工作集"""
        
    def add_set(self):
        """新建空工作集"""
        
    def get_fiducial_closest_to(self, x, y, working_set=None):
        """獲取離指定點最近的基準點
        
        Parameters:
            x,y (float): 目標點坐標
            working_set (int): 工作集索引,None表示搜索所有工作集
        Returns:
            tuple(int, Fiducial): (工作集索引, 基準點對象)"""
```

#### 使用範例

1. 基本基準點操作:
```python
from zygo.fiducials import Fiducials
from zygo.units import Units

# 創建基準點管理器
fiducials = Fiducials()

# 載入基準點文件
fiducials.load("d:/fiducials/my_fiducials.fid")

# 獲取基準點數量
sets = fiducials.get_num_sets()
print(f"Working sets: {sets}")

# 遍歷所有基準點
for set_index, fiducial in fiducials:
    print(f"Working set {set_index}:")
    print(f"  Center: {fiducial.center}")
    print(f"  Size: {fiducial.width}x{fiducial.height}")
```

2. 基準點移動和旋轉:
```python
# 獲取最接近指定點的基準點
set_idx, fiducial = fiducials.get_fiducial_closest_to(100, 100)

# 移動基準點
fiducial.move_absolute(150, 150)  # 移動到絕對位置
fiducial.move_relative(10, 10)    # 相對移動

# 旋轉基準點45度
fiducial.rotate(45, Units.Degrees)
```

3. 工作集管理:
```python
# 新建工作集
fiducials.add_set()

# 清空指定工作集
fiducials.clear_set(0)

# 刪除整個工作集
fiducials.delete_set(1)

# 保存所有基準點
fiducials.save("d:/fiducials/modified_fiducials.fid")
```

### 13. 圖表控制 (Charts Control)

圖表控制模組提供了對MX圖表的軸和限制值進行操作的功能。

#### 圖表類型定義

```python
class ChartAxis(IntEnum):
    """圖表軸定義"""
    X = 1      # X軸
    Y = 2      # Y軸
    All = 3    # 所有軸

class ChartLimit(IntEnum):
    """限制值類型定義"""
    Low = 1    # 下限
    High = 2   # 上限 
    All = 3    # 所有限制
```

#### 限制值設置函數

**clear_chart_limit(control, axis_name=ChartAxis.All, limit_name=ChartLimit.All)**
- 功能：清除圖表限制值
- 參數：
  - control (Control): 圖表控件
  - axis_name (ChartAxis): 要清除的軸
  - limit_name (ChartLimit): 要清除的限制類型

**set_chart_high_limit(control, axis_name=ChartAxis.Y, limit_value=0, unit=Units.MicroMeters)**
- 功能：設置圖表上限值
- 參數：
  - control (Control): 圖表控件
  - axis_name (ChartAxis): 要設置的軸
  - limit_value (float): 上限值
  - unit (Units): 單位

**set_chart_low_limit(control, axis_name=ChartAxis.Y, limit_value=0, unit=Units.MicroMeters)**  
- 功能：設置圖表下限值
- 參數：
  - control (Control): 圖表控件
  - axis_name (ChartAxis): 要設置的軸
  - limit_value (float): 下限值
  - unit (Units): 單位

**set_chart_limits(control, axis_name=ChartAxis.Y, low_value=0, high_value=100, unit=Units.MicroMeters)**
- 功能：同時設置上下限值
- 參數：
  - control (Control): 圖表控件
  - axis_name (ChartAxis): 要設置的軸
  - low_value (float): 下限值
  - high_value (float): 上限值
  - unit (Units): 單位

#### 使用範例

1. 清除圖表限制:
```python
from zygo._charts import clear_chart_limit, ChartAxis, ChartLimit

# 清除Y軸的所有限制
clear_chart_limit(
    control=chart_control,
    axis_name=ChartAxis.Y,
    limit_name=ChartLimit.All
)

# 清除所有軸的所有限制
clear_chart_limit(
    control=chart_control,
    axis_name=ChartAxis.All,
    limit_name=ChartLimit.All
)
```

2. 設置單個限制值:
```python
from zygo._charts import set_chart_high_limit, set_chart_low_limit
from zygo.units import Units

# 設置Y軸上限值
set_chart_high_limit(
    control=chart_control,
    axis_name=ChartAxis.Y,
    limit_value=100,
    unit=Units.MicroMeters
)

# 設置X軸下限值
set_chart_low_limit(
    control=chart_control, 
    axis_name=ChartAxis.X,
    limit_value=0,
    unit=Units.MicroMeters
)
```

3. 同時設置上下限:
```python
from zygo._charts import set_chart_limits
from zygo.units import Units

# 設置Y軸的顯示範圍為0-100微米
set_chart_limits(
    control=chart_control,
    axis_name=ChartAxis.Y,
    low_value=0,
    high_value=100,
    unit=Units.MicroMeters
)
```

注意事項:
1. 圖表控制函數都需要一個圖表控件(Control)對象作為參數
2. 如果不指定axis_name，默認操作Y軸
3. 單位默認使用微米(MicroMeters)
4. 清除限制值時可以選擇清除單個軸的單個限制，也可以一次清除所有限制

### 14. QDAS統計分析 (QDAS Statistics)

QDAS模組提供了與Q-DAS統計過程控制(SPC)系統的整合功能。

#### 研究類型定義

```python
class QdasStudyType(IntEnum):
    """QDAS研究類型"""
    standard = 0        # 標準生產
    type_1 = 1         # Type 1研究
    type_2 = 2         # Type 2研究 
    type_3 = 3         # Type 3研究

class OperationPromptType(IntEnum):
    """操作提示類型"""
    none = 0           # 無提示
    info = 1           # 信息提示
    serial = 2         # 序列號提示
    unique_serial = 3  # 唯一序列號提示
```

#### 測試計劃操作

**create_qdas_testplan(testplan_path=None, qdas_params_path=None, auto_kfields=None)**
- 功能：創建Q-DAS測試計劃
- 參數：
  - testplan_path (str): 測試計劃文件路徑
  - qdas_params_path (str): QDAS參數文件路徑 
  - auto_kfields (list): 自動添加的K字段列表
- 返回：新創建的測試計劃路徑

**export_qdas_results(testplan_path=None, qdas_results_path=None, auto_kfields=None, study_type=QdasStudyType.standard, silent=False)**
- 功能：導出QDAS結果
- 參數：
  - testplan_path (str): 測試計劃文件路徑
  - qdas_results_path (str): 結果文件路徑
  - auto_kfields (dict): K字段和值字典
  - study_type (QdasStudyType): 研究類型
  - silent (bool): 是否靜默模式
- 返回：導出操作結果

#### 研究執行

**do_standard(spc_testplan, testplan_info, operation, auto_kfields=None)**
- 功能：執行標準生產研究
- 參數：
  - spc_testplan (str): SPC測試計劃路徑
  - testplan_info (dict): 測試計劃信息
  - operation (func): 每次迭代執行的操作
  - auto_kfields (dict): 自動K字段

**do_type_1(spc_testplan, testplan_info, operation, auto_kfields=None, prompt=OperationPromptType.info, sequence_start=None)**
- 功能：執行Type 1量規研究
- 參數：
  - spc_testplan (str): SPC測試計劃路徑
  - testplan_info (dict): 測試計劃信息
  - operation (func): 每次迭代執行的操作
  - auto_kfields (dict): 自動K字段
  - prompt (OperationPromptType): 提示類型
  - sequence_start (int): 序列號起始值

**do_type_2(spc_testplan, testplan_info, operation, auto_kfields=None, prompt=OperationPromptType.info, sequence_start=None)**  
- 功能：執行Type 2量規研究
- 參數與Type 1研究相同

#### 特徵值類 (QdasCharacteristic)

```python
class QdasCharacteristic:
    """QDAS特徵值定義"""
    
    @property
    def uid(self):
        """獲取唯一ID"""
        
    @property
    def name(self):
        """獲取特徵值名稱"""
        
    @property
    def groupname(self):
        """獲取分組名稱"""
        
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

#### 使用範例

1. 創建測試計劃:
```python 
from zygo.qdas import create_qdas_testplan

# 創建新的測試計劃
testplan = create_qdas_testplan(
    testplan_path="d:/testplans/my_testplan.TestPlan",
    qdas_params_path="d:/params/params.csv",
    auto_kfields=["K1001", "K2001"] 
)
```

2. 執行標準研究:
```python
from zygo.qdas import do_standard, QdasStudyType

# 定義測量操作
def measure():
    # 執行測量...
    pass

# 執行標準研究
do_standard(
    spc_testplan="testplan.TestPlan",
    testplan_info=testplan_info,
    operation=measure,
    auto_kfields={"K1001": "VALUE1"}
)
```

3. 執行Type 1研究:
```python
from zygo.qdas import do_type_1, OperationPromptType

# 執行Type 1研究
do_type_1(
    spc_testplan="testplan.TestPlan",
    testplan_info=testplan_info,  
    operation=measure,
    prompt=OperationPromptType.info,
    sequence_start=1000
)
```

### 15. 連接管理 (Connection Management)### 5. 運動控制 (Motion Control)

運動控制模組提供了對Zygo儀器各軸運動的完整控制功能。

#### 軸類型定義

```python 
class AxisType(IntEnum):
    """軸名稱定義"""
    unknown = 0  # 未知軸
    x = 1        # X軸
    y = 2        # Y軸
    z = 3        # Z軸
    rx = 4       # Pitch軸(繞X軸旋轉)
    ry = 5       # Roll軸(繞Y軸旋轉)
    rz = 6       # Theta軸(繞Z軸旋轉)
    x2 = 7       # 第二X軸
    y2 = 8       # 第二Y軸
    z2 = 9       # 第二Z軸
    rx2 = 10     # 第二Pitch軸
    ry2 = 11     # 第二Roll軸
    rz2 = 12     # 第二Theta軸
```

```python
class StageType(IntEnum):
    """平台類型定義"""
    stage_all = 0  # 所有平台
    stage1 = 1     # 平台1
    stage2 = 2     # 平台2
```

#### 位置獲取

**基本軸位置獲取:**

```python
def get_x_pos(unit, stage=StageType.stage1):
    """獲取X軸位置
    
    Parameters:
        unit (Units): 返回值的單位
        stage (StageType): 平台選擇
    Returns: 
        float: X軸位置"""

def get_y_pos(unit, stage=StageType.stage1):
    """獲取Y軸位置"""
    
def get_z_pos(unit, stage=StageType.stage1):
    """獲取Z軸位置"""
```

**角度軸位置獲取:**

```python
def get_p_pos(unit, stage=StageType.stage1):
    """獲取Pitch軸位置"""
    
def get_r_pos(unit, stage=StageType.stage1):
    """獲取Roll軸位置"""
    
def get_t_pos(unit, stage=StageType.stage1):
    """獲取Theta軸位置"""
```

#### 運動控制

**單軸運動:**

```python
def move_x(x_pos, unit, wait=True, stage=StageType.stage1):
    """移動X軸到指定位置
    
    Parameters:
        x_pos (float): 目標位置
        unit (Units): 位置單位
        wait (bool): 是否等待運動完成
        stage (StageType): 平台選擇
    Returns:
        ZygoTask: 運動任務對象"""

def move_y(y_pos, unit, wait=True, stage=StageType.stage1):
    """移動Y軸到指定位置"""
    
def move_z(z_pos, unit, wait=True, stage=StageType.stage1):
    """移動Z軸到指定位置"""
```

**多軸聯動:**

```python
def move_xy(x_pos, y_pos, unit, wait=True, stage=StageType.stage1):
    """同時移動X軸和Y軸"""
    
def move_xyz(x_pos, y_pos, z_pos, unit, wait=True, stage=StageType.stage1):
    """同時移動X、Y、Z三軸"""
```

**角度軸運動:**

```python
def move_p(p_pos, unit, wait=True, parcentric=False, stage=StageType.stage1):
    """移動Pitch軸,可選擇是否使用parcentric補償"""
    
def move_r(r_pos, unit, wait=True, parcentric=False, stage=StageType.stage1):
    """移動Roll軸,可選擇是否使用parcentric補償"""
    
def move_t(t_pos, unit, wait=True, stage=StageType.stage1):
    """移動Theta軸"""
```

#### 回原點操作

**單軸回原:**
```python
def home_x(wait=True, stage=StageType.stage1):
    """X軸回原點"""
    
def home_y(wait=True, stage=StageType.stage1):
    """Y軸回原點"""
    
def home_z(wait=True, stage=StageType.stage1):
    """Z軸回原點"""
```

**多軸同時回原:**
```python
def home_xy(wait=True, stage=StageType.stage1):
    """X、Y軸同時回原點"""
    
def home_xyz(wait=True, stage=StageType.stage1):
    """X、Y、Z軸同時回原點"""
    
def home_all(wait=True, stage=StageType.stage_all):
    """所有軸回原點"""
```

#### 運動狀態控制

**等待運動完成:**
```python
def wait(axes, timeout=None):
    """等待指定軸運動完成
    
    Parameters:
        axes (AxisType/list): 要等待的軸
        timeout (int): 超時時間(毫秒),None表示無限等待"""
```

**狀態查詢:**
```python
def is_active(axis):
    """檢查軸是否可用"""
    
def is_homed(axis):
    """檢查軸是否已回原點"""
    
def is_zstop_set():
    """檢查Z軸是否設置了停止點"""
```

**手動控制面板:**
```python
def set_pendant_enabled(enabled):
    """啟用/禁用手動控制面板
    
    Parameters:
        enabled (bool): True啟用,False禁用"""
```

#### 使用範例

1. 基本位置獲取:
```python
from zygo.motion import get_x_pos, get_y_pos
from zygo.units import Units

# 獲取當前XY位置(單位:微米)
x = get_x_pos(Units.MicroMeters)
y = get_y_pos(Units.MicroMeters)
print(f"Current position: X={x}μm, Y={y}μm")
```

2. 單軸運動:
```python
from zygo.motion import move_x
from zygo.units import Units

# 移動X軸到100微米位置
move_x(100, Units.MicroMeters, wait=True)
```

3. 多軸聯動:
```python
from zygo.motion import move_xyz
from zygo.units import Units

# 同時移動XYZ到指定位置
move_xyz(100, 200, 50, Units.MicroMeters, wait=True)
```

4. 回原點操作:
```python
from zygo.motion import home_all

# 所有軸回原點
home_all(wait=True)
```

### 6. 配方管理 (Recipe Management)

配方管理模組提供了對Zygo MX配方(Recipe)的基本操作功能。

#### 主要功能

**save(filename)**
- 功能：保存當前配方到文件
- 參數：
  - filename (str): 保存的文件路徑

**load(filename)**  
- 功能：從文件載入配方
- 參數：
  - filename (str): 配方文件路徑

**run()**
- 功能：執行當前載入的配方
- 無參數

#### 使用範例

```python
from zygo.recipe import load, run, save

# 載入配方
load("d:/recipes/my_measurement.recipe")

# 執行配方
run()

# 保存修改後的配方
save("d:/recipes/my_measurement_modified.recipe")
```

### 7. 掩模管理 (Masks Management)

掩模管理模組提供了對Zygo MX中掩模(Mask)的完整操作功能。

#### 掩模類 (Mask Class)

```python
class Mask:
    """代表單個MX掩模"""
    
    @property
    def center(self):
        """獲取掩模中心坐標(Point2D對象)"""
        
    @property
    def height(self):
        """獲取掩模高度"""
        
    @property
    def width(self):
        """獲取掩模寬度"""
        
    @property
    def type(self):
        """獲取掩模類型"""
        
    def move_absolute(self, x, y):
        """移動掩模中心到指定絕對位置
        
        Parameters:
            x (float): 新的X坐標
            y (float): 新的Y坐標"""
            
    def move_relative(self, x, y):
        """按相對距離移動掩模中心
        
        Parameters:
            x (float): X方向移動距離
            y (float): Y方向移動距離"""
            
    def resize(self, height, width):
        """調整掩模尺寸
        
        Parameters:
            height (float): 新的高度
            width (float): 新的寬度"""
            
    def rotate(self, value, unit):
        """旋轉掩模
        
        Parameters:
            value (float): 旋轉角度
            unit (Units): 角度單位"""
```

#### 掩模集合類 (Masks Class)

```python
class Masks:
    """代表MX掩模集合"""
    
    def get_num_masks(self, mask_type=None):
        """獲取指定類型掩模的數量
        
        Parameters:
            mask_type (str): 掩模類型,None表示所有類型
        Returns:
            int: 掩模數量"""
            
    def save(self, filename):
        """保存掩模到文件"""
        
    def load(self, filename):
        """從文件載入掩模"""
        
    def delete(self, mask):
        """刪除指定掩模"""
        
    def clear(self, mask_type=None):
        """清除指定類型的所有掩模"""
        
    def get_mask_closest_to(self, x, y, mask_type=None):
        """獲取離指定點最近的掩模
        
        Parameters:
            x,y (float): 目標點坐標
            mask_type (str): 掩模類型,None表示所有類型
        Returns:
            Mask: 最近的掩模對象"""
```

#### 使用範例

1. 基本掩模操作:
```python
from zygo.masks import Masks
from zygo.units import Units

# 創建掩模管理器
masks = Masks()

# 載入掩模文件
masks.load("d:/masks/my_masks.msk")

# 獲取掩模數量
count = masks.get_num_masks()
print(f"Total masks: {count}")

# 遍歷所有掩模
for mask in masks:
    print(f"Mask type: {mask.type}")
    print(f"Center position: {mask.center}")
    print(f"Size: {mask.width}x{mask.height}")
```

2. 掩模移動和旋轉:
```python
# 獲取最接近指定點的掩模
mask = masks.get_mask_closest_to(100, 100)

# 移動掩模
mask.move_absolute(150, 150)  # 移動到絕對位置
mask.move_relative(10, 10)    # 相對移動

# 旋轉掩模45度
mask.rotate(45, Units.Degrees)
```

3. 保存和清理:
```python
# 保存當前掩模
masks.save("d:/masks/modified_masks.msk")

# 清除所有掩模
masks.clear()
```

### 8. 中止操作 (Abort Operation)

中止操作模組提供了立即停止當前MX命令執行的功能。

#### 主要功能

**abort()**
- 功能：中止當前正在執行的MX命令
- 無參數
- 說明：此函數會傳送中止信號給當前進程，立即停止正在執行的MX操作

#### 使用範例

```python
from zygo.abort import abort

try:
    # 執行某些MX操作...
    
    # 如果需要,可以中止操作
    if error_condition:
        abort()
        print("Operation aborted")
except Exception as e:
    # 發生錯誤時中止
    abort()
    print(f"Error occurred: {str(e)}")
```

使用注意事項：
1. abort()函數會立即中止當前操作,應謹慎使用
2. 建議在try-except塊中使用,以確保出錯時能正確中止
3. 中止後可能需要重新初始化某些操作

### 9. 圖案管理 (Pattern Management)

圖案管理模組提供了對MX圖案(Pattern)和圖像拼接(Stitch)功能的操作。

#### 基本圖案操作

**save(filename)**
- 功能：保存當前圖案到文件
- 參數：
  - filename (str): 保存的文件路徑

**load(filename)**  
- 功能：從文件載入圖案
- 參數：
  - filename (str): 圖案文件路徑

**run()**
- 功能：執行當前圖案
- 無參數

#### 拼接相關操作

**load_stitch(filename)**
- 功能：載入拼接設置
- 參數：
  - filename (str): 拼接設置文件路徑

**load_and_stitch(folder)**
- 功能：載入指定文件夾中的數據並執行拼接
- 參數：
  - folder (str): 數據文件夾路徑

#### 對齊操作

**prealign()**
- 功能：對當前圖案執行預對齊
- 無參數

**align()**
- 功能：對當前圖案執行對齊
- 無參數

#### 使用範例

1. 基本圖案操作:
```python
from zygo.pattern import load, run, save

# 載入圖案
load("d:/patterns/measurement_pattern.pat")

# 執行圖案
run()

# 保存修改後的圖案
save("d:/patterns/modified_pattern.pat")
```

2. 拼接操作:
```python
from zygo.pattern import load_and_stitch

# 載入數據並執行拼接
load_and_stitch("d:/measurement_data")
```

3. 對齊流程:
```python
from zygo.pattern import load, prealign, align

# 載入圖案
load("d:/patterns/alignment_pattern.pat")

# 執行預對齊
prealign()

# 執行最終對齊
align()
```

### 10. 連接管理 (Connection Management)# Zygo MX Python API 技術文檔

## 概述
Zygo MX Python API 是一個用於控制和自動化Zygo顯微鏡系統的Python庫。該庫提供了全面的功能來操作和分析測量數據。

## 系統需求
- Python 3.4.3
- Windows 操作系統 (基於系統信息顯示為Windows 10 Enterprise 2016 LTSB)
- Zygo MX 軟件安裝

## 主要模組結構

### 0. 核心功能 (Core Functionality)

這個模組提供了Zygo MX腳本的核心功能實現。

#### 錯誤處理
```python
class ZygoError(Exception):
    """Zygo MX或連接產生的異常"""
    pass
```

#### 異步任務處理
```python
class ZygoTask(object):
    """代表異步Zygo MX操作的任務對象"""
    
    @property
    def done(self):
        """檢查任務是否完成"""
        
    def wait(self, timeout=None):
        """等待任務完成
        timeout: 最大等待時間(毫秒),None表示無限等待"""
        
    def result(self, timeout=None):
        """獲取任務結果
        timeout: 最大等待時間(毫秒),None表示無限等待
        returns: 操作結果,無結果則返回None"""
```

#### 2D點坐標
```python
class Point2D(object):
    """定義(x,y)坐標空間中的點
    
    參數:
    x (int/float): X坐標
    y (int/float): Y坐標
    """
```

### 1. 使用者界面控制 (UI Control)

這個模組提供了對Zygo MX軟件界面的控制功能。

#### 對話框控制

```python
class DialogMode(IntEnum):
    """對話框模式,定義顯示的按鈕和圖標"""
    message_ok = 1
    error_ok = 2 
    warning_ok = 3
    confirm_yes_no = 4
    error_ok_cancel = 5
    warning_yes_no = 6
    message_ok_cancel = 7
```

**show_dialog(text, mode, seconds=None, title=None, message_font=None, button_font=None)**
- 功能：顯示對話框
- 參數：
  - text (str): 對話框訊息文字
  - mode (DialogMode): 對話框模式
  - seconds (int): 顯示時間(秒),None為等待用戶響應
  - title (str): 對話框標題
  - message_font (Font): 訊息字體
  - button_font (Font): 按鈕字體
- 返回：布爾值(用戶響應結果)

**show_input_dialog(text, default_value, mode, ...)**
- 功能：顯示輸入對話框
- 參數：
  - text (str): 提示文字
  - default_value (str): 默認值
  - mode (DialogMode): 對話框模式
  - max_length (int): 最大輸入長度
- 返回：str (用戶輸入值)

#### 視窗控制

```python
class Window:
    """代表MX GUI視窗"""
    
    @property
    def controls(self):
        """獲取視窗中的所有控件"""
        
    def close(self):
        """關閉視窗"""
        
    def save_data(self, file_path):
        """保存視窗數據到文件"""
        
    def save_image(self, file_path):
        """保存視窗截圖到文件"""
```

#### 控件操作

```python
class Control:
    """代表MX GUI控件"""
    
    @property
    def controls(self):
        """獲取子控件"""
        
    def save_data(self, file_path, optional_params=None):
        """保存控件數據到文件"""
        
    def save_image(self, file_path):
        """保存控件截圖到文件"""
        
    def click_toolbar_item(self, path):
        """點擊工具欄項目"""
```

#### 容器操作

```python
class Container:
    """代表MX GUI容器"""
    
    @property
    def controls(self):
        """獲取容器中的所有控件"""
        
    @property
    def plots(self):
        """獲取容器中的所有繪圖控件"""
        
    def show(self):
        """顯示容器"""
```

#### Tab頁面控制

```python
class Tab:
    """代表MX GUI標籤頁"""
    
    def show(self):
        """顯示標籤頁"""
        
    @property
    def groups(self):
        """獲取標籤頁中的所有分組"""
        
    @property
    def dock_panels(self):
        """獲取標籤頁中的所有停靠面板"""
```

### 3. 系統命令 (System Commands)

系統命令模組提供了對Zygo MX主機系統的基本操作功能。

#### 文件類型
```python
class FileTypes(Enum):
    """MX支持的文件類型"""
    All = ()                     # 所有文件
    UI_Application = ()          # UI應用程序
    Script = ()                  # 腳本文件
    Csv = ()                     # CSV文件
    Data = ()                    # 數據文件
    Signal_Data = ()             # 信號數據
    Setting = ()                 # 設置文件
    Image = ()                   # 圖像文件
    Recipe = ()                  # 配方文件
    Result = ()                  # 結果文件
    Mask = ()                    # 掩模文件
    # ... 更多文件類型
```

#### 目錄操作

**get_bin_dir()**
- 功能：獲取MX可執行文件所在目錄
- 返回：MX bin目錄的絕對路徑

**get_working_dir()**
- 功能：獲取MX進程當前工作目錄
- 返回：工作目錄的絕對路徑

**get_open_dir(file_type)**
- 功能：獲取指定文件類型的打開目錄
- 參數：
  - file_type (FileTypes): 文件類型
- 返回：打開目錄的絕對路徑

**get_save_dir(file_type)**
- 功能：獲取指定文件類型的保存目錄
- 參數：
  - file_type (FileTypes): 文件類型
- 返回：保存目錄的絕對路徑

**set_open_dir(file_type, path)**
- 功能：設置指定文件類型的打開目錄
- 參數：
  - file_type (FileTypes): 文件類型
  - path (str): 目錄絕對路徑

**set_save_dir(file_type, path)**
- 功能：設置指定文件類型的保存目錄
- 參數：
  - file_type (FileTypes): 文件類型
  - path (str): 目錄絕對路徑

#### 文件操作

**list_files_in_open_dir(file_type)**
- 功能：列出指定類型的打開目錄中的所有文件
- 參數：
  - file_type (FileTypes): 文件類型
- 返回：文件絕對路徑列表

**list_files_in_dir(directory, extensions, recursive=False)**
- 功能：列出指定目錄中匹配指定擴展名的文件
- 參數：
  - directory (str): 搜索目錄
  - extensions (list): 擴展名列表
  - recursive (bool): 是否遞歸搜索子目錄
- 返回：文件絕對路徑列表

#### 主機信息

**get_ram_size()**
- 功能：獲取分配給MX的私有內存大小(字節)
- 返回：內存大小(整數)

**get_os_name()**
- 功能：獲取MX主機的操作系統名稱
- 返回：操作系統名稱

**get_computer_name()**
- 功能：獲取MX主機的計算機名稱
- 返回：計算機名稱

#### 使用範例
```python
from zygo.systemcommands import FileTypes, get_save_dir, list_files_in_dir

# 獲取數據文件的保存目錄
data_dir = get_save_dir(FileTypes.Data)
print(f"Data files are saved to: {data_dir}")

# 列出目錄中的所有.dat文件
dat_files = list_files_in_dir(data_dir, [".dat"], recursive=True)
for file in dat_files:
    print(f"Found data file: {file}")
```

### 4. 連接管理 (Connection Management)

連接管理模組負責處理與Zygo MX儀器的通信連接。

#### 基本連接操作

**connect(force_if_active=False, host='localhost', port=8733, uid='')**
- 功能：建立與MX的連接
- 參數：
  - force_if_active (bool): 即使當前服務狀態為Active也強制連接
  - host (str): 主機名或IP地址
  - port (int): 端口號
  - uid (str): 連接的唯一標識符
- 返回：連接的唯一標識符(uid)

**terminate()**
- 功能：關閉與MX的連接
- 無參數

**get_service_state()**
- 功能：獲取當前服務狀態
- 返回：WebServiceState枚舉值
```python
class WebServiceState(IntEnum):
    none = 0    # 無狀態
    idle = 1    # 空閒
    active = 2  # 活動
```

#### 連接狀態管理

**get_uid()**
- 功能：獲取當前連接的唯一標識符
- 返回：uid字符串

**get_is_remote_access_connected()**
- 功能：檢查是否有遠程訪問客戶端連接
- 返回：布爾值

**set_is_sequence_step(is_sequence_step)**
- 功能：設置當前腳本是否作為序列步驟運行
- 參數：
  - is_sequence_step (bool): 是否為序列步驟

#### HTTP請求處理

**send_request(service, method, params=None, *, decode=True)**
- 功能：發送HTTP請求並等待響應
- 參數：
  - service (str): 服務名稱
  - method (str): 方法名稱
  - params (dict): 輸入參數字典
  - decode (bool): 是否解碼JSON響應
- 返回：字典或字符串形式的響應

**get_send_request(service, method, params=None, *, decode=True)**
- 功能：發送HTTP請求並提取返回值
- 參數與send_request相同
- 返回：直接返回方法的返回值

#### 錯誤處理
```python
class ZygoError(Exception):
    """Zygo MX或連接產生的異常"""
    pass
```

#### 使用範例
```python
from zygo.connectionmanager import connect, terminate

try:
    # 連接到本地MX服務器
    uid = connect(host='localhost', port=8733)
    print(f"Connected with UID: {uid}")
    
    # 執行操作...
    
finally:
    # 確保連接被關閉
    terminate()
```

### 4. 使用者界面控制 (UI Control)

Zygo MX支持豐富的測量單位系統，所有可用的單位都定義在`Units`枚舉類中。

#### 常用基本單位

**線性測量單位:**
- Angstroms (埃) 
- MicroMeters (微米)
- MilliMeters (毫米)
- Meters (米)
- Inches (英寸)
- MicroInches (微英寸)
- Mils (密爾)
- NanoMeters (納米)

**角度單位:**
- Degrees (度)
- ArcMinutes (角分)
- ArcSeconds (角秒)
- Radians (弧度)
- MicroRadians (微弧度)
- MilliRadians (毫弧度)

**面積單位:**
- SquareMicroMeters (平方微米)
- SquareMilliMeters (平方毫米)
- SquareMeters (平方米)
- SquareInches (平方英寸)

**體積單位:**  
- CubicMicroMeters (立方微米)
- CubicMilliMeters (立方毫米)
- CubicMeters (立方米)
- CubicInches (立方英寸)

#### 特殊測量單位

**非物理高度單位:**
- Waves (波長)
- UserWaves (用戶波長)
- Fringes (條紋)
- FringeRadians (條紋弧度)

**非物理橫向單位:**
- Pixels (像素)

**頻率單位:**
- Hertz (赫茲)
- KiloHertz (千赫茲)
- MegaHertz (兆赫茲)
- GigaHertz (吉赫茲)

**時間單位:**
- MicroSeconds (微秒)
- MilliSeconds (毫秒)
- Seconds (秒)
- Minutes (分鐘)
- Hours (小時)

**相機相關:**
- Counts (計數)

**其他:**
- Invalid - 無效單位
- NotSet - 未設置單位
- NoUnits - 無單位
- Scaled - 縮放單位

#### 使用範例

```python
from zygo.units import Units

# 獲取結果時指定單位
result = get_result_number(("Results", "Peak"), unit=Units.MicroMeters)

# 設置值時指定單位
set_control_number(("Process", "Height"), 1.5, unit=Units.MilliMeters)
```

單位驗證:
```python
def _validate_unit(unit):
    """驗證輸入是否為有效的單位值
    
    Parameters
    ----------
    unit : Units or str
        要驗證的單位
        
    Returns
    -------
    str
        單位的字符串表示
        
    Raises
    ------
    TypeError
        如果輸入不是 Units 或 str 類型
    ValueError  
        如果輸入字符串不能轉換為有效的 Units 成員
    """
```

### 3. 儀器控制 (Instrument Control)

這個模組提供了直接控制Zygo儀器的功能。主要包含以下功能類別：

#### 數據採集 (Data Acquisition)

**acquire(wait=True)**
- 功能：在主機儀器上獲取數據
- 參數：
  - wait (bool): 是否等待採集完成
- 返回：AcquisitionTask 對象

**measure(wait=True)**
- 功能：測量數據（相當於acquire後跟analyze）
- 參數：
  - wait (bool): 是否等待測量完成
- 返回：AcquisitionTask 對象

#### 自動優化功能

- **auto_focus()** - 執行自動對焦
- **auto_tilt()** - 執行自動傾斜調整
- **auto_focus_tilt()** - 執行自動對焦和傾斜調整
- **auto_light_level()** - 執行自動光照水平調整
- **auto_lat_cal(value, unit)** - 執行自動橫向校準

#### 硬件控制

**轉台控制：**
- get_turret() - 獲取當前轉台位置
- move_turret(position) - 移動轉台到指定位置

**變焦控制：**
- get_zoom() - 獲取當前變焦值
- set_zoom(zoom) - 設置變焦值
- get_min_zoom() - 獲取最小變焦值
- get_max_zoom() - 獲取最大變焦值
- lock_zoom() - 鎖定變焦
- unlock_zoom() - 解鎖變焦

**光照控制：**
- get_light_level() - 獲取當前光照水平
- set_light_level(light_level) - 設置光照水平

**對焦控制：**
- get_encoded_focus() - 獲取當前編碼器對焦位置
- set_encoded_focus(focus) - 設置編碼器對焦位置
- lock_encoded_focus() - 鎖定編碼器對焦
- unlock_encoded_focus() - 解鎖編碼器對焦

#### 模式控制

**對齊/查看模式：**
```python
class AlignViewMode(IntEnum):
    none = 0  # 未知或無效
    align = 1  # 對齊模式
    view = 2   # 查看模式
```
- get_align_view_mode() - 獲取當前模式
- set_align_view_mode(mode) - 設置模式

**環/點模式：**
```python
class RingSpotMode(IntEnum):
    none = 0  # 未知或無效
    ring = 1  # 環模式
    spot = 2  # 點模式
```
- get_ring_spot_mode() - 獲取當前模式
- set_ring_spot_mode(mode) - 設置模式

#### 相機信息

- get_cam_res(unit) - 獲取相機分辨率
- get_cam_size_x(unit) - 獲取相機寬度
- get_cam_size_y(unit) - 獲取相機高度

#### 系統信息

- get_system_serial_number() - 獲取系統序列號
- get_system_type() - 獲取系統類型
- set_sleep_mode_enabled(enabled) - 啟用/禁用睡眠模式

### 1. 應用程序控制 (Application Control)
這些方法用於控制Zygo MX應用程序的基本操作：

#### 核心方法：

**is_application_open()**
- 功能：檢查MX應用程序是否開啟
- 返回值：布爾值（True/False）

**get_application_path()**
- 功能：獲取當前應用程序的完整路徑
- 返回值：字符串（路徑）或None（如果未打開）

**open_application(filename)**
- 功能：打開指定的MX應用程序
- 參數：
  - filename (str): MX應用程序文件路徑

**close_application()**
- 功能：關閉當前MX應用程序
- 無參數

**save_application_as(filename)**
- 功能：將當前MX應用程序保存為指定文件
- 參數：
  - filename (str): 保存路徑

### 2. 數據操作 (Data Operations)

#### 基本數據操作：

**analyze()**
- 功能：分析當前數據
- 無參數

**load_data(filename)**
- 功能：加載MX數據文件
- 參數：
  - filename (str): 數據文件路徑

**save_data(filename)**
- 功能：保存當前MX數據到指定文件
- 參數：
  - filename (str): 保存路徑

#### 高級數據操作：

**subtract_data(filename, ignore_lateral_res=True, use_input_size=False, use_system_size=False, use_fiducial_alignment=False, alignment_type=FiducialAlignmentType.fixed, alignment_tolerance=1.0)**
- 功能：從當前數據中減去指定文件的數據
- 參數：
  - filename (str): 要減去的數據文件路徑
  - ignore_lateral_res (bool): 是否忽略橫向分辨率
  - use_input_size (bool): 是否使用輸入矩陣數據大小
  - use_system_size (bool): 是否使用系統參考數據大小
  - use_fiducial_alignment (bool): 是否使用基準對齊
  - alignment_type (FiducialAlignmentType): 對齊類型
  - alignment_tolerance (float): 對齊容差（像素）

**scale_data(scale_value)**
- 功能：縮放當前數據
- 參數：
  - scale_value (float): 縮放因子

### 3. 結果和控制 (Results and Controls)

#### 獲取值：

**get_result_number(path, unit=None)**
- 功能：獲取指定結果的數值
- 參數：
  - path (tuple of str): 結果路徑
  - unit (Units): 期望的單位（可選）
- 返回值：float（所請求單位的結果值）

**get_control_string(path)**
- 功能：獲取指定控制的字符串值
- 參數：
  - path (tuple of str): 控制路徑
- 返回值：str（控制值）

#### 設置值：

**set_result_number(path, value, unit=None)**
- 功能：設置指定結果的數值
- 參數：
  - path (tuple of str): 結果路徑
  - value (float): 要設置的值
  - unit (Units): 值的單位（可選）

**set_control_string(path, value)**
- 功能：設置指定控制的字符串值
- 參數：
  - path (tuple of str): 控制路徑
  - value (str): 要設置的值

### 4. 設置操作 (Settings Operations)

**load_settings(filename)**
- 功能：加載MX設置文件
- 參數：
  - filename (str): 設置文件路徑

**save_settings(filename)**
- 功能：保存當前MX設置到文件
- 參數：
  - filename (str): 保存路徑

### 5. 日誌記錄 (Logging)

提供多個級別的日誌記錄方法：

- log_trace(message)
- log_debug(message)
- log_info(message)
- log_warn(message)
- log_error(message)
- log_fatal(message)

每個方法參數：
- message (str): 要記錄的消息

### 6. 注釋管理 (Annotations)

**create_annotation(name, value)**
- 功能：創建新的MX注釋
- 參數：
  - name (str): 注釋名稱
  - value (str): 注釋值

**get_annotation(path)**
- 功能：獲取指定MX注釋的值
- 參數：
  - path (tuple of str): 注釋路徑
- 返回值：str（注釋值）

### 7. 數據矩陣操作 (Data Matrix Operations)

提供了一系列方法來獲取和操作數據矩陣的幾何特性：

**get_data_center_x/y(control, unit)**
- 功能：獲取指定繪圖控件的幾何中心x/y坐標
- 參數：
  - control (ui.Control): 繪圖控件
  - unit (Units): 所需坐標值的單位
- 返回值：float（請求單位的坐標值）

**get_data_size_x/y(control, unit)**
- 功能：獲取指定繪圖控件的寬度/高度
- 參數：
  - control (ui.Control): 繪圖控件
  - unit (Units): 所需尺寸的單位
- 返回值：float（請求單位的尺寸值）

## 常見用例

### 1. 基本測量流程
```python
# 打開應用程序
open_application("path/to/mx/app.mx")

# 載入設置
load_settings("path/to/settings.xml")

# 執行測量和分析
analyze()

# 保存結果
save_data("path/to/results.dat")
```

### 2. 數據處理
```python
# 載入並平均多個數據文件
load_and_average_data(
    ["file1.dat", "file2.dat", "file3.dat"],
    min_valid_pct=80,
    use_fiducial_alignment=True
)

# 處理數據
scale_data(1.5)  # 放大1.5倍
trim_data(10)    # 修剪邊緣
```

### 3. 自動化分析流程
```python
# 打開應用程序
open_application("analysis.mx")

# 設置控制參數
set_control_number(("Process", "Threshold"), 0.5)
set_control_string(("Analysis", "Mode"), "Standard")

# 執行分析
analyze()

# 獲取結果
result = get_result_number(("Results", "Peak"), unit="micrometers")
print(f"Peak value: {result} µm")
```

## 注意事項
1. 所有涉及文件操作的路徑都必須是Windows格式的路徑
2. 單位參數需要使用庫中定義的Units枚舉值
3. 路徑參數通常需要以元組形式提供，例如：("Process", "Settings", "Value")
4. 部分功能可能需要特定的Zygo硬件支持

## 錯誤處理
庫中的大多數方法在失敗時會拋出異常，應該使用try-except塊來處理可能的錯誤：

```python
try:
    open_application("app.mx")
except Exception as e:
    log_error(f"Failed to open application: {str(e)}")
```

## 版本信息
可以使用 `get_mx_version()` 方法獲取MX軟件版本。

## 參考資料
- Zygo MX 軟件文檔
- Python 3.4.3 文檔