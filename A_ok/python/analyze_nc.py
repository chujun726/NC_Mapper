import os
import xarray as xr
import sys
from typing import Optional, List


def coor_name_list_of_nc(nc_file_path: str) -> list:
    """
    回傳 nc_file 中的所有軸的名稱列表。

    Args:
        nc_file_path: str
            NetCDF 檔案的路徑。

    Returns:
        coordinate_name_list: list
            軸的名稱列表。
    """
    # check user input
    if not isinstance(nc_file_path, str):
        raise TypeError("nc_file_path must be a string")
    nc_file_path = os.path.abspath(nc_file_path)
    if not os.path.exists(nc_file_path):
        raise FileNotFoundError(f"{nc_file_path} not found")

    # read NetCDF file and get coordinate names
    with xr.open_dataset(nc_file_path) as dataset:
        coordinate_name_list = list(dataset.coords.keys())

    return coordinate_name_list


def var_list_of_nc(nc_file_path: str) -> list:
    """
    回傳 nc_file 中的所有變數的名稱列表。

    Args:
        nc_file_path: str
            NetCDF 檔案的路徑。

    Returns:
        var_list: list
            變數的名稱列表。
    """
    # check user input
    if not isinstance(nc_file_path, str):
        raise TypeError("nc_file_path must be a string")
    nc_file_path = os.path.abspath(nc_file_path)
    if not os.path.exists(nc_file_path):
        raise FileNotFoundError(f"{nc_file_path} not found")

    # read NetCDF file and get variable names
    with xr.open_dataset(nc_file_path) as dataset:
        var_list = list(dataset.data_vars.keys())

    return var_list


def coor_name_list_of_var(nc_file_path: str, variable_name: str) -> list:
    """
    回傳 nc_file 中 variable_name 變數的所有軸的名稱列表。

    Args:
        nc_file_path: str
            NetCDF 檔案的路徑。
        variable_name: str
            變數的名稱。

    Returns:
        coordinate_name_list: list
            軸的名稱列表。
    """
    # check user input
    if not isinstance(nc_file_path, str):
        raise TypeError("nc_file_path must be a string")
    nc_file_path = os.path.abspath(nc_file_path)
    if not os.path.exists(nc_file_path):
        raise FileNotFoundError(f"{nc_file_path} not found")
    if not isinstance(variable_name, str):
        raise TypeError("variable_name must be a string")
    if variable_name not in var_list_of_nc(nc_file_path):
        raise ValueError(f"{variable_name} not found in {nc_file_path}")

    # read NetCDF file and get coordinate names of variable
    with xr.open_dataset(nc_file_path) as dataset:
        coordinate_name_list = list(dataset[variable_name].coords.keys())

    return coordinate_name_list


def height_list_of_var(nc_file_path: str, variable_name: str, z_coor_name: Optional[str]) -> List:
    """
    回傳 nc_file 中 variable_name 變數的 z_coor_name 軸的所有高度列表。

    Args:
        nc_file_path: str
            NetCDF 檔案的路徑。
        variable_name: str
            變數的名稱。
        z_coor_name: str|None
            高度軸的名稱，若為 None 則無高度軸。

    Returns:
        height_list: list
            高度列表。
    """
    # check user input
    if not isinstance(nc_file_path, str):
        raise TypeError("nc_file_path must be a string")
    nc_file_path = os.path.abspath(nc_file_path)
    if not os.path.exists(nc_file_path):
        raise FileNotFoundError(f"{nc_file_path} not found")
    if not isinstance(variable_name, str):
        raise TypeError("variable_name must be a string")
    if variable_name not in var_list_of_nc(nc_file_path):
        raise ValueError(f"{variable_name} not found in {nc_file_path}")
    if not isinstance(z_coor_name, str) and z_coor_name is not None:
        raise TypeError("z_coor_name must be a string")

    # if z_coor_name is None, return empty list
    if z_coor_name is None:
        return []

    # if z_coor_name not in coor_name_list_of_var, raise error
    if z_coor_name not in coor_name_list_of_var(nc_file_path, variable_name):
        return []

    # read NetCDF file and get height list of variable
    with xr.open_dataset(nc_file_path) as dataset:
        height_list = list(dataset[z_coor_name].values)

    return height_list

if __name__ == "__main__":
    if len(sys.argv) == 1:
        
        print('測試')
        
        print("coor_name_list_of_nc('data/sample.nc')：")
        print(coor_name_list_of_nc("data/sample.nc"))
        print("----")
        # coor_name_list_of_nc('data/sample.nc')：
        # ['latitude', 'level', 'time', 'longitude']
        # ----

        print("var_list_of_nc('data/sample.nc')：")
        print(var_list_of_nc("data/sample.nc"))
        print("----")
        # var_list_of_nc('data/sample.nc')：
        # ['2m_temperature', 'geopotential']
        # ----

        print("coor_name_list_of_var('data/sample.nc', '2m_temperature')：")
        print(coor_name_list_of_var("data/sample.nc", "2m_temperature"))
        print("coor_name_list_of_var('data/sample.nc', 'geopotential')：")
        print(coor_name_list_of_var("data/sample.nc", "geopotential"))
        print("----")
        # coor_name_list_of_var('data/sample.nc', '2m_temperature')：
        # ['latitude', 'time', 'longitude']
        # coor_name_list_of_var('data/sample.nc', 'geopotential')：
        # ['latitude', 'level', 'time', 'longitude']

        print("height_list_of_var('data/sample.nc', '2m_temperature', 'level')：")
        print(height_list_of_var("data/sample.nc", "2m_temperature", "level"))
        print("height_list_of_var('data/sample.nc', 'geopotential', 'level')：")
        print(height_list_of_var("data/sample.nc", "geopotential", "level"))
        print("----")
        # ----
        # height_list_of_var('data/sample.nc', '2m_temperature', 'level')：
        # []
        # height_list_of_var('data/sample.nc', 'geopotential', 'level')：
        # [1000, 900, 800, 500, 300]
    
    # 新增：處理命令行參數的情況
    
    elif len(sys.argv) == 2:
        print("請在指令中輸入欲獲得的資料選項")
    
    elif len(sys.argv) == 3:
        try:
            nc_file_path = sys.argv[1] # 指令中0為脚本、1為nc檔、2為欲獲得的資料選項
            # 檢查檔案是否存在
            if not os.path.exists(nc_file_path):
                raise FileNotFoundError(f"找不到檔案：{nc_file_path}")
            command = sys.argv[2]
            
            # Step2: 獲取維度列表
            if command == "dimensions":
                dimensions = coor_name_list_of_nc(nc_file_path)
                for dim in dimensions:
                    print(dim)
                    
            # Step3：變量選擇
            elif command == "variables":
                variables = var_list_of_nc(nc_file_path)
                for var in variables:
                    print(var)
            else:
                print(f"未知的命令：{command}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    elif len(sys.argv) == 4:
        try:
            nc_file_path = sys.argv[1]
            command = sys.argv[2]
            variable = sys.argv[3]

            if not os.path.exists(nc_file_path):
                raise FileNotFoundError(f"找不到檔案：{nc_file_path}")

            if command == "heights":
                # 假設使用 'level' 作為高度維度的名稱
                heights = height_list_of_var(nc_file_path, variable, 'level')
                for height in heights:
                    print(height)
            else:
                print(f"未知的命令：{command}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)