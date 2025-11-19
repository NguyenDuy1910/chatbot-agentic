# Connection Type Modal Feature

## Tổng quan
Thay vì chuyển trang khi bấm nút "New Connection", giờ đây hệ thống sẽ hiển thị một modal popup để người dùng chọn loại connection muốn tạo.

## Các thay đổi

### 1. Component mới: `ConnectionTypeModal.tsx`
- Hiển thị danh sách các loại connection có sẵn (Database, API, Webhook, OAuth, File Storage, etc.)
- Grid layout với icons đẹp mắt và mô tả chi tiết
- Có tính năng tìm kiếm để filter các loại connection
- Responsive design với nhiều breakpoints (1, 2, 3 cột)

### 2. Cập nhật `ConnectionDashboard.tsx`
- Import component `ConnectionTypeModal`
- Thêm state `isTypeModalOpen` để quản lý việc hiển thị modal
- Thêm state `selectedConnectionType` để lưu loại connection đã chọn
- Thêm handler `handleSelectConnectionType` để xử lý khi người dùng chọn loại connection
- Cập nhật button "New Connection" để mở modal thay vì chuyển trang trực tiếp
- Render modal component trong return statement

## Các loại Connection được hỗ trợ

1. **Database** - Connect to SQL/NoSQL databases
2. **REST API** - Connect to REST APIs
3. **Webhook** - Receive real-time events
4. **OAuth** - Authenticate with OAuth 2.0
5. **File Storage** - Connect to cloud storage (S3, GCS, etc.)
6. **Messaging** - Connect to message queues
7. **Analytics** - Connect to analytics platforms
8. **Payment** - Connect to payment gateways
9. **Email** - Connect to email services
10. **SMS** - Connect to SMS services
11. **Social Media** - Connect to social platforms
12. **CRM** - Connect to CRM systems
13. **ERP** - Connect to ERP systems
14. **Custom** - Create a custom connection

## User Flow

1. Người dùng bấm button "New Connection"
2. Modal popup hiển thị với danh sách các loại connection
3. Người dùng có thể:
   - Tìm kiếm loại connection bằng search bar
   - Click vào một loại connection để chọn
   - Click "Cancel" để đóng modal
4. Sau khi chọn loại connection, hệ thống sẽ chuyển đến `ConnectionWorkflow` để tạo connection

## UI/UX Improvements

- **Modal size**: 5xl (rất rộng) để hiển thị đầy đủ các options
- **Scroll behavior**: inside - cho phép scroll trong modal khi có nhiều items
- **Visual feedback**: 
  - Hover effects với shadow và border color
  - Scale animation khi hover vào icon
  - Gradient colors cho từng loại connection
- **Accessibility**: 
  - Keyboard navigation
  - Clear visual hierarchy
  - Descriptive labels

## Technical Details

### Dependencies
- `@heroui/react`: Modal, Card, Button, Input components
- `lucide-react`: Icons cho mỗi loại connection

### State Management
- `isTypeModalOpen`: Boolean state để control việc hiển thị modal
- `selectedConnectionType`: String state để lưu type đã chọn
- Sử dụng `useDisclosure` hook từ HeroUI để quản lý modal state

### Props Interface

```typescript
interface ConnectionTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectType: (typeId: string) => void;
}
```

## Future Enhancements

1. Add more connection types as needed
2. Show connection templates for each type
3. Add popular/recommended badges for common types
4. Show connection count for each type
5. Add filters by category (Data, Communication, Business, etc.)
