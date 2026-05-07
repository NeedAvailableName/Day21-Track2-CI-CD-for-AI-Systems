# BÁO CÁO THỰC HÀNH MLOPS (LAB 21)

## 1. Kết quả huấn luyện (Bước 1)

### Bộ siêu tham số đã chọn:
- **Thuật toán**: `random_forest`
- **n_estimators**: 1000
- **max_depth**: 30
- **min_samples_split**: 2
- **min_samples_leaf**: 1

### Lý do lựa chọn:
Qua quá trình thực nghiệm và tối ưu hóa (Grid Search), bộ tham số này cho phép mô hình có đủ khả năng học các đặc trưng phức tạp của tập dữ liệu Wine Quality. Khi kết hợp với việc bổ sung dữ liệu ở Bước 3 (từ 2,998 lên 5,996 mẫu), độ chính xác (accuracy) đã tăng đáng kể từ **0.68** lên **0.76**, vượt qua ngưỡng yêu cầu (0.70) của pipeline.

---

## 2. Khó khăn gặp phải và Cách giải quyết

### 2.1. Lỗi xác thực DVC (401 Unauthorized)
- **Vấn đề**: Pipeline GitHub Actions không thể `dvc pull` do lỗi credentials.
- **Giải pháp**: 
    - Sửa lỗi cú pháp trong file `.dvc/config` (header sai định dạng).
    - Xóa đường dẫn cứng `credentialpath` để DVC ưu tiên sử dụng biến môi trường `GOOGLE_APPLICATION_CREDENTIALS`.
    - Sử dụng khối `env` trong GitHub Workflow để truyền secret an toàn hơn, tránh lỗi nội dung JSON.

### 2.2. Lỗi cơ sở dữ liệu MLflow (Alembic Revision Error)
- **Vấn đề**: MLflow không thể khởi động do xung đột phiên bản database (`mlflow.db`).
- **Giải pháp**: Xóa file `mlflow.db` cũ và để MLflow tự động khởi tạo lại database sạch.

### 2.3. Lỗi Push Git do file quá lớn (> 100MB)
- **Vấn đề**: Vô tình commit các artifact của MLflow (file `model.pkl` trong `mlruns/`) có kích thước lên tới 200MB, khiến GitHub từ chối lệnh push.
- **Giải pháp**: 
    - Cập nhật `.gitignore` để loại bỏ thư mục `mlruns/`.
    - Sử dụng `git reset --mixed` để xóa các commit lỗi khỏi lịch sử và thực hiện commit lại chỉ với các file mã nguồn cần thiết.

### 2.4. Lỗi kết nối SSH đến VM
- **Vấn đề**: `appleboy/ssh-action` thất bại với lỗi `unable to authenticate`.
- **Giải pháp**: 
    - Thực hiện lệnh `gcloud compute ssh` để đẩy public key (`mlops_deploy.pub`) vào file `authorized_keys` của VM.
    - Kiểm tra và cập nhật chính xác secret `VM_USER` (tài khoản cá nhân trên VM) thay vì dùng email của service account.

---

## 3. Thách thức nâng cao (Bonus)
Tôi đã hoàn thành cả 5 nhiệm vụ Bonus:
1. **Bonus 1**: Cấu hình pipeline hỗ trợ DagsHub MLflow tracking.
2. **Bonus 2**: Hỗ trợ nhiều thuật toán (RandomForest, GradientBoosting, LogisticRegression).
3. **Bonus 3**: Tự động tạo và upload báo cáo `report.txt` (Confusion Matrix & Classification Report).
4. **Bonus 4**: Thiết lập cơ chế **Rollback Safety Gate**: Chỉ deploy model mới nếu accuracy không bị giảm so với model hiện tại.
5. **Bonus 5**: Tự động kiểm tra và cảnh báo lệch lạc dữ liệu (Data Imbalance) ngay trong log huấn luyện.
