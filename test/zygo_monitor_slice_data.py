from zygo import mx
from zygo.slices import (
    LinearSliceType,
    RadialSliceType,
    CircularSliceType,
    get_all_linear_slices,
    get_all_radial_slices,
    get_all_circular_slices
)
from zygo.units import Units
from zygo import ui
import json
from datetime import datetime


def get_slice_data(slice_control):
    """獲取所有類型的切片數據"""
    try:
        results = {
            'timestamp': datetime.now().isoformat(),
            'linear_slices': {},
            'radial_slices': {},
            'circular_slices': {}
        }

        # 獲取線性切片數據
        linear_slices = get_all_linear_slices(slice_control)
        for label, slice in linear_slices.items():
            # 獲取基本信息
            length = slice.get_length(Units.MicroMeters)
            angle = slice.get_angle(Units.Degrees)
            midpoint = slice.get_midpoint(Units.MicroMeters)
            start, end = slice.get_endpoints(Units.MicroMeters)

            results['linear_slices'][label] = {
                'length': length,
                'angle': angle,
                'midpoint': {'x': midpoint.x, 'y': midpoint.y},
                'start': {'x': start.x, 'y': start.y},
                'end': {'x': end.x, 'y': end.y}
            }

            print(f"\n線性切片 {label}:")
            print(f"  長度: {length} μm")
            print(f"  角度: {angle} 度")
            print(f"  中點: ({midpoint.x}, {midpoint.y})")
            print(f"  起點: ({start.x}, {start.y})")
            print(f"  終點: ({end.x}, {end.y})")

        # 獲取徑向切片數據
        radial_slices = get_all_radial_slices(slice_control)
        for label, slice in radial_slices.items():
            length = slice.get_length(Units.MicroMeters)
            angle = slice.get_angle(Units.Degrees)
            start = slice.get_start(Units.MicroMeters)

            results['radial_slices'][label] = {
                'length': length,
                'angle': angle,
                'start': {'x': start.x, 'y': start.y}
            }

            print(f"\n徑向切片 {label}:")
            print(f"  長度: {length} μm")
            print(f"  角度: {angle} 度")
            print(f"  起點: ({start.x}, {start.y})")

        # 獲取圓形切片數據
        circular_slices = get_all_circular_slices(slice_control)
        for label, slice in circular_slices.items():
            radius = slice.get_radius(Units.MicroMeters)
            center = slice.get_center(Units.MicroMeters)

            results['circular_slices'][label] = {
                'radius': radius,
                'center': {'x': center.x, 'y': center.y}
            }

            print(f"\n圓形切片 {label}:")
            print(f"  半徑: {radius} μm")
            print(f"  圓心: ({center.x}, {center.y})")

        return results

    except Exception as e:
        print(f"獲取切片數據時出錯: {str(e)}")
        mx.log_error(f"獲取切片數據時出錯: {str(e)}")
        raise


def main():
    try:
        # 檢查應用程序是否開啟
        if not mx.is_application_open():
            raise Exception("Zygo應用程序未開啟")

        print("正在獲取切片控制項...")

        # 獲取切片控制項
        slice_control = ui.get_control(("ANALYZE", "Surface", "Surface", "3D Surface Data", "sliceControl1"))
        print("成功獲取切片控制項")

        # 獲取切片數據
        print("\n開始獲取切片數據...")
        slice_data = get_slice_data(slice_control)

        # 將數據保存為JSON文件(可選)
        with open('slice_data.json', 'w', encoding='utf-8') as f:
            json.dump(slice_data, f, ensure_ascii=False, indent=2)
            print("\n數據已保存到 slice_data.json")

    except Exception as e:
        print(f"程序執行出錯: {str(e)}")
        mx.log_error(f"程序執行出錯: {str(e)}")


if __name__ == "__main__":
    main()