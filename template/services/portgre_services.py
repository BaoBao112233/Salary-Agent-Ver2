"""
Script test để insert dữ liệu nhân viên vào PostgreSQL
Chạy sau khi đã start docker-compose up -d
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from template.configs.environments import env

# Thông tin kết nối database
DB_CONFIG = {
    "host": env.PORTGRES_HOST,
    "port": env.PORTGRES_PORT,
    "user": env.PORTGRES_USER,
    "password": env.PORTGRES_PASSWORD,
    "database": env.PORTGRES_DB
}

def create_table():
    """Tạo bảng employees nếu chưa tồn tại"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    create_query = """
    CREATE TABLE IF NOT EXISTS employees (
        ma_nhan_vien VARCHAR(20) PRIMARY KEY,
        ho_va_ten VARCHAR(100) NOT NULL,
        so_ngay_cong_thuc_te INTEGER,
        so_gio_lam_them INTEGER,
        so_ngay_nghi_phep INTEGER,
        so_ngay_nghi_khong_luong INTEGER,
        so_lan_di_muon INTEGER,
        so_lan_ve_som INTEGER,
        du_an VARCHAR(100),
        phong_ban VARCHAR(100),
        he_so_thu_viec FLOAT,
        chuc_danh VARCHAR(100),
        luong_co_ban BIGINT,
        luong_dong_bhxh BIGINT,
        thuong_co_dinh BIGINT,
        phu_cap_chuc_vu BIGINT,
        phu_cap_xang_xe BIGINT,
        phu_cap_dien_thoai BIGINT,
        phu_cap_com BIGINT,
        so_nguoi_phu_thuoc INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cur.execute(create_query)
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Đã tạo bảng employees")

def insert_employee_data(data):
    """Insert dữ liệu nhân viên vào database (có thể là 1 dict hoặc list of dicts)"""
    # Xử lý nếu data là list
    if isinstance(data, list):
        success_count = 0
        for employee in data:
            try:
                _insert_single_employee(employee)
                success_count += 1
            except Exception as e:
                print(f"⚠️ Lỗi insert nhân viên {employee.get('Mã nhân viên', 'N/A')}: {str(e)}")
        print(f"✓ Đã insert {success_count}/{len(data)} nhân viên vào database")
        return success_count
    else:
        # Xử lý nếu data là single dict
        return _insert_single_employee(data)

def _insert_single_employee(data):
    """Insert 1 nhân viên vào database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Debug: Log first employee's keys
    import logging
    logger = logging.getLogger(__name__)
    if 'NV001' in str(data.get('Mã nhân viên', '')):
        logger.info(f"Sample employee keys: {list(data.keys())}")
    
    insert_query = """
    INSERT INTO employees (
        ma_nhan_vien, ho_va_ten, so_ngay_cong_thuc_te, so_gio_lam_them,
        so_ngay_nghi_phep, so_ngay_nghi_khong_luong, so_lan_di_muon,
        so_lan_ve_som, du_an, phong_ban, he_so_thu_viec, chuc_danh,
        luong_co_ban, luong_dong_bhxh, thuong_co_dinh, phu_cap_chuc_vu,
        phu_cap_xang_xe, phu_cap_dien_thoai, phu_cap_com, so_nguoi_phu_thuoc
    ) VALUES (
        %(Mã nhân viên)s, %(Họ và tên)s, %(Số ngày công thực tế)s, 
        %(Số giờ làm thêm)s, %(Số ngày nghỉ phép)s, %(Số ngày nghỉ không lương)s,
        %(Số lần đi muộn)s, %(Số lần về sớm)s, %(Dự án)s, %(Phòng ban)s,
        %(Hệ số thử việc)s, %(Chức danh)s, %(Lương cơ bản)s, %(Lương đóng BHXH)s,
        %(Thưởng cố định)s, %(Phụ cấp chức vụ)s, %(Phụ cấp xăng xe)s,
        %(Phụ cấp điện thoại)s, %(Phụ cấp cơm)s,
        %(Số người phụ thuộc)s
    )
    ON CONFLICT (ma_nhan_vien) DO UPDATE SET
        ho_va_ten = EXCLUDED.ho_va_ten,
        so_ngay_cong_thuc_te = EXCLUDED.so_ngay_cong_thuc_te,
        so_gio_lam_them = EXCLUDED.so_gio_lam_them
    """
    
    cur.execute(insert_query, data)
    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ Đã insert nhân viên: {data['Mã nhân viên']} - {data['Họ và tên']}")
    return 1