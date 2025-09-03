# AuthSystem - Comprehensive Astro Authentication & User Management

A modern, secure authentication and user management system built with Astro, featuring JWT authentication, role-based access control, and a beautiful UI.

![Landing Page](https://github.com/user-attachments/assets/d69eb627-c221-4011-9c2d-01efff71e536)

![Admin Dashboard](https://github.com/user-attachments/assets/5241c898-50bc-454c-923d-c68f5a939faa)

## ✨ Features

### 🔐 Authentication System
- **JWT-based Authentication** with secure token handling
- **User Registration** with email verification support
- **Password Reset** functionality via email
- **Session Management** with automatic token refresh
- **Route Protection** middleware for authenticated routes
- **Remember Me** functionality for persistent sessions

### 👥 User Management
- **User Dashboard** showing profile and activity
- **Profile Management** for editing user information and changing passwords
- **Admin Panel** for comprehensive user administration
- **Role-based Access Control** (user/admin roles)
- **Account Settings** and status management

### 🎨 Modern UI/UX
- **Responsive Design** with mobile-first approach using Tailwind CSS
- **Dark/Light Mode** theme switching
- **Loading States** and skeleton screens
- **Form Validation** with helpful error messages
- **Toast Notifications** for user feedback

### 🛡️ Security Features
- **Password Hashing** using bcrypt with salt rounds
- **CSRF Protection** for form submissions
- **Rate Limiting** to prevent brute force attacks
- **Input Sanitization** and XSS protection
- **Secure Headers** configuration
- **Audit Logging** for user activities

### 🗄️ Database Integration
- **SQLite Database** with Drizzle ORM
- **Migration System** for schema management
- **Connection Pooling** for efficient database handling
- **Type-safe Database Operations**

### 📧 External Integrations
- **Email Service** setup with Resend (configurable)
- **File Upload** support with Cloudinary (configurable)
- **Account Verification** system

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd astro-auth-system
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
# Database
DATABASE_URL="file:./local.db"

# JWT Secrets (CHANGE THESE IN PRODUCTION!)
JWT_SECRET="your-super-secret-jwt-key-change-in-production"
JWT_REFRESH_SECRET="your-super-secret-refresh-key-change-in-production"

# Email Service (Resend)
RESEND_API_KEY="your-resend-api-key"
FROM_EMAIL="noreply@yourdomain.com"

# File Upload (Cloudinary)
CLOUDINARY_CLOUD_NAME="your-cloudinary-cloud-name"
CLOUDINARY_API_KEY="your-cloudinary-api-key"
CLOUDINARY_API_SECRET="your-cloudinary-api-secret"

# Application
BASE_URL="http://localhost:4321"
NODE_ENV="development"
```

4. **Set up the database**
```bash
# Generate migration files
npm run db:generate

# Run migrations
npx tsx migrate.ts
```

5. **Create admin user (optional)**
```bash
npx tsx seed.ts
```

This creates:
- **Admin User**: admin@example.com / admin123
- **Test User**: user@example.com / user123

6. **Start the development server**
```bash
npm run dev
```

Visit `http://localhost:4321` to see your application!

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication-related components
│   ├── ui/             # Basic UI components (Button, Input, Card)
│   ├── admin/          # Admin panel components
│   └── layout/         # Layout components (Navigation, etc.)
├── pages/              # Astro pages and API routes
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # User dashboard
│   ├── admin/          # Admin panel pages
│   └── api/            # API endpoints
│       ├── auth/       # Authentication APIs
│       ├── user/       # User management APIs
│       └── admin/      # Admin APIs
├── middleware/         # Authentication middleware
├── utils/              # Utility functions and services
├── lib/                # Core libraries (auth, database)
├── types/              # TypeScript type definitions
└── styles/             # Global styles
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `PUT /api/user/change-password` - Change user password

### Admin Management
- `GET /api/admin/users` - List all users (paginated)
- `GET /api/admin/users/:id` - Get specific user
- `PUT /api/admin/users/:id` - Update user
- `DELETE /api/admin/users/:id` - Delete user

## 🛠️ Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run db:generate  # Generate database migrations
npm run db:migrate   # Run database migrations
npm run db:studio    # Open Drizzle Studio (database GUI)
```

### Database Management

The project uses Drizzle ORM with SQLite. To make schema changes:

1. Modify the schema in `src/lib/schema.ts`
2. Generate migration: `npm run db:generate`
3. Apply migration: `npx tsx migrate.ts`

### Adding New Features

1. **API Routes**: Add new endpoints in `src/pages/api/`
2. **Pages**: Create new pages in `src/pages/`
3. **Components**: Add reusable components in `src/components/`
4. **Utilities**: Add helper functions in `src/utils/`

## 🔒 Security Considerations

### In Production
1. **Change all default secrets** in environment variables
2. **Use HTTPS** for all communications
3. **Configure proper CORS** settings
4. **Set up proper email service** (Resend/SendGrid)
5. **Configure file upload service** (Cloudinary/AWS S3)
6. **Set up monitoring** and logging
7. **Regular security updates** for dependencies

### Rate Limiting
- Login attempts: 5 attempts per 15 minutes
- API requests: 100 requests per minute
- Password reset: 3 attempts per hour

## 🚀 Deployment

### Prerequisites
- Node.js 18+ runtime
- Environment variables configured
- Database accessible

### Build & Deploy
```bash
# Build the application
npm run build

# The built application is in the dist/ folder
# Deploy dist/ to your hosting provider
```

### Environment Variables for Production
Ensure all environment variables are properly set in your production environment, especially:
- `JWT_SECRET` and `JWT_REFRESH_SECRET` (strong, unique values)
- `DATABASE_URL` (production database)
- `RESEND_API_KEY` (for emails)
- `CLOUDINARY_*` (for file uploads)
- `BASE_URL` (your production domain)
- `NODE_ENV=production`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Astro](https://astro.build/) - The web framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Drizzle ORM](https://orm.drizzle.team/) - TypeScript ORM
- [Zod](https://zod.dev/) - TypeScript-first schema validation

---

**Built with ❤️ using Astro and modern web technologies**