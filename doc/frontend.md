# Frontend Documentation

## Overview

SCRIPT's frontend is built with Angular 16, providing an interactive, responsive interface for the intelligent tutoring system. The application uses Angular Material for UI components and Monaco Editor for code editing.

---

## Technology Stack

- **Framework**: Angular 16
- **UI Library**: Angular Material
- **Code Editor**: Monaco Editor
- **Markdown**: ngx-markdown with KaTeX for math
- **State Management**: RxJS
- **Routing**: Angular Router
- **HTTP**: Angular HttpClient

---

## Project Structure

```
frontend/its_ui/
├── src/
│   ├── app/
│   │   ├── admin-settings/        # Admin configuration UI
│   │   ├── auth/                  # Authentication components
│   │   ├── code-panel/            # Monaco editor wrapper
│   │   ├── course-selection-panel/ # Course selection UI
│   │   ├── course-settings/       # Course settings for tutors
│   │   ├── feedback-panel/        # Feedback display
│   │   ├── navigation-bar/        # Top navigation
│   │   ├── profile/               # User profile
│   │   ├── shared/                # Shared services & models
│   │   ├── skill-overview/        # Skill progress visualization
│   │   ├── task-panel/            # Task description display
│   │   ├── app-routing.module.ts  # Route configuration
│   │   ├── app.component.*        # Root component
│   │   └── app.module.ts          # Main module
│   ├── assets/                    # Static assets
│   ├── environments/              # Environment configs
│   ├── styles.css                 # Global styles
│   └── index.html                 # HTML entry point
├── angular.json                   # Angular configuration
├── package.json                   # Dependencies
└── tsconfig.json                  # TypeScript config
```

---

## Core Components

### 1. App Component

**Location**: `src/app/app.component.ts`

Root component that bootstraps the application.

**Responsibilities:**
- Initialize app-level services
- Handle routing outlet
- Manage global state

### 2. Navigation Bar

**Location**: `src/app/navigation-bar/`

Top navigation with user menu and course information.

**Features:**
- User profile access
- Course selection link
- Logout functionality
- Responsive design

**Routes:**
- Profile: `/profile`
- Course Selection: `/course-selection`
- Course Settings: `/course-settings`
- Admin Settings: `/admin-settings` (admin only)

### 3. Authentication Components

**Location**: `src/app/auth/`

Handle user authentication flows.

**Components:**
- `LoginComponent`: User login
- `RegisterComponent`: New user registration
- `VerifyEmailComponent`: Email verification
- `ForgotPasswordComponent`: Password reset request
- `ResetPasswordComponent`: Password reset with token

**Services:**
- `AuthService`: Manages authentication state
- JWT token storage in localStorage
- HTTP interceptor for auth headers

**Example Usage:**
```typescript
constructor(private authService: AuthService) {}

async login() {
  const result = await this.authService.login(
    this.username, 
    this.password
  );
  if (result.success) {
    this.router.navigate(['/course-selection']);
  }
}
```

### 4. Course Selection Panel

**Location**: `src/app/course-selection-panel/`

Browse and enroll in courses.

**Features:**
- Display available courses
- Show course metadata (domain, topics)
- Enroll in new courses
- Continue existing courses
- Upload courses (admin/tutor)

**Data Flow:**
```
Component → CourseService → API → Backend
                ↓
        Update local state
                ↓
        Display courses
```

### 5. Task Panel

**Location**: `src/app/task-panel/`

Display task descriptions with markdown rendering.

**Features:**
- Markdown rendering with syntax highlighting
- LaTeX math rendering (KaTeX)
- Image support
- Responsive layout

**Dependencies:**
- `ngx-markdown`: Markdown parsing
- `katex`: Math rendering

**Example:**
```typescript
@Component({
  selector: 'app-task-panel',
  template: `
    <markdown [data]="taskDescription" katex></markdown>
  `
})
export class TaskPanelComponent {
  taskDescription: string;
}
```

### 6. Code Panel

**Location**: `src/app/code-panel/`

Monaco editor wrapper for code editing.

**Features:**
- Syntax highlighting (Python, JavaScript, etc.)
- Auto-completion
- Error highlighting
- Code formatting
- Vim/Emacs keybindings (optional)

**Configuration:**
```typescript
editorOptions = {
  theme: 'vs-dark',
  language: 'python',
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 14,
  wordWrap: 'on'
};
```

**State Tracking:**
- Debounced change tracking (500ms)
- Diff computation for attempts
- Auto-save to backend

### 7. Feedback Panel

**Location**: `src/app/feedback-panel/`

Display various types of feedback.

**Feedback Types:**
1. **Test Results**: Unit test pass/fail
2. **Run Output**: stdout/stderr from code execution
3. **AI Feedback**: LLM-generated suggestions
4. **State-Space Feedback**: Expert state guidance

**UI Elements:**
- Tabbed interface for different feedback types
- Syntax-highlighted code snippets
- Error messages with line numbers
- Collapsible sections

### 8. Profile Component

**Location**: `src/app/profile/`

User profile and settings management.

**Features:**
- Display user information
- Update username
- Change password
- Data collection preferences
- Research consent settings

**Data Collection Options:**
- **Detailed Logging**: Track all code edits
- **Research Usage**: Allow data in publications

### 9. Admin Settings

**Location**: `src/app/admin-settings/`

System-wide configuration (admin only).

**Settings:**
- LLM API type (Ollama/OpenAI)
- API URL and key
- Email configuration
- System information

**Guard:**
```typescript
{
  path: 'admin-settings',
  component: AdminSettingsComponent,
  canActivate: [AdminGuard]
}
```

### 10. Course Settings

**Location**: `src/app/course-settings/`

Course-specific settings (tutor/admin).

**Features:**
- Update pedagogical model
- Configure feedback timing
- Upload new tasks
- Manage course visibility

---

## Services

### AuthService

**Location**: `src/app/shared/services/auth.service.ts`

Handles authentication and authorization.

**Methods:**
```typescript
login(username: string, password: string): Promise<LoginResult>
logout(): void
register(userData: UserCreate): Promise<RegisterResult>
verifyEmail(token: string): Promise<VerifyResult>
requestPasswordReset(email: string): Promise<void>
resetPassword(token: string, newPassword: string): Promise<void>
isAuthenticated(): boolean
getToken(): string | null
getCurrentUser(): Observable<User>
```

### CourseService

**Location**: `src/app/shared/services/course.service.ts`

Manages course data and enrollment.

**Methods:**
```typescript
getCourses(): Observable<Course[]>
getCourse(uniqueName: string): Observable<Course>
selectCourse(uniqueName: string): Promise<void>
uploadCourse(courseData: FormData): Promise<void>
getCourseSettings(uniqueName: string): Observable<CourseSettings>
updateCourseSettings(settings: CourseSettings): Promise<void>
```

### TaskService

**Location**: `src/app/shared/services/task.service.ts`

Handles task retrieval and navigation.

**Methods:**
```typescript
getNextTask(topic?: string): Observable<Task>
getTaskByName(uniqueName: string): Observable<Task>
markTaskCompleted(uniqueName: string): Promise<void>
```

### SubmissionService

**Location**: `src/app/shared/services/submission.service.ts`

Manages code submissions and execution.

**Methods:**
```typescript
submitCode(taskUniqueName: string, code: string): Promise<SubmissionResult>
runCode(taskUniqueName: string, code: string, stdin: string): Promise<RunResult>
requestFeedback(taskUniqueName: string, code: string): Promise<FeedbackResult>
getSubmissionFeedback(submissionId: string): Observable<Feedback>
```

### AttemptService

**Location**: `src/app/shared/services/attempt.service.ts`

Tracks code attempts and state changes.

**Methods:**
```typescript
getAttemptState(taskUniqueName: string): Observable<AttemptState>
updateAttemptState(attemptId: string, lineUpdate: LineUpdate): Promise<void>
```

---

## State Management

SCRIPT uses RxJS observables for reactive state management.

### Example: Task State

```typescript
// In component
export class TutoringComponent implements OnInit {
  currentTask$: Observable<Task>;
  currentCode: string = '';
  
  constructor(private taskService: TaskService) {}
  
  ngOnInit() {
    this.currentTask$ = this.taskService.getNextTask();
    
    this.currentTask$.subscribe(task => {
      this.loadAttemptState(task.unique_name);
    });
  }
  
  async loadAttemptState(taskUniqueName: string) {
    const state = await this.attemptService.getAttemptState(taskUniqueName);
    this.currentCode = state.code;
  }
}
```

### Shared State

For global state, use BehaviorSubjects in services:

```typescript
@Injectable({ providedIn: 'root' })
export class UserStateService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();
  
  setCurrentUser(user: User) {
    this.currentUserSubject.next(user);
  }
}
```

---

## Routing

### Route Configuration

**File**: `src/app/app-routing.module.ts`

```typescript
const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'verify', component: VerifyEmailComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { 
    path: 'course-selection', 
    component: CourseSelectionComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'tutoring', 
    component: TutoringComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'profile', 
    component: ProfileComponent,
    canActivate: [AuthGuard]
  },
  { 
    path: 'course-settings', 
    component: CourseSettingsComponent,
    canActivate: [AuthGuard, TutorGuard]
  },
  { 
    path: 'admin-settings', 
    component: AdminSettingsComponent,
    canActivate: [AuthGuard, AdminGuard]
  },
  { path: '**', redirectTo: '/login' }
];
```

### Guards

**AuthGuard**: Requires authentication
```typescript
@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  canActivate(): boolean {
    return this.authService.isAuthenticated();
  }
}
```

**AdminGuard**: Requires admin role
```typescript
@Injectable({ providedIn: 'root' })
export class AdminGuard implements CanActivate {
  canActivate(): boolean {
    const user = this.authService.getCurrentUser();
    return user?.roles?.includes('admin') ?? false;
  }
}
```

---

## Styling

### Global Styles

**File**: `src/styles.css`

- Angular Material theme
- Custom CSS variables
- Typography
- Layout utilities

**Example:**
```css
:root {
  --primary-color: #3f51b5;
  --accent-color: #ff4081;
  --background-color: #fafafa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
```

### Component Styles

Use component-scoped styles:

```typescript
@Component({
  selector: 'app-task-panel',
  templateUrl: './task-panel.component.html',
  styleUrls: ['./task-panel.component.css']
})
```

### Angular Material Theming

**File**: `src/styles.css`

```css
@import '~@angular/material/prebuilt-themes/indigo-pink.css';

/* Custom theme overrides */
.mat-toolbar {
  background-color: var(--primary-color);
}
```

---

## HTTP Interceptors

### Auth Interceptor

Automatically adds JWT token to requests.

```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const token = this.authService.getToken();
    
    if (token) {
      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(req);
  }
}
```

### Error Interceptor

Handles HTTP errors globally.

```typescript
@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    return next.handle(req).pipe(
      catchError(error => {
        if (error.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
        }
        return throwError(error);
      })
    );
  }
}
```

---

## Build & Deployment

### Development Build

```bash
ng serve
# Runs on http://localhost:4200
```

### Production Build

```bash
ng build --configuration production
# Output in dist/its_ui/
```

### Docker Build

**Dockerfile**:
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/its_ui /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Testing

### Unit Tests

```bash
ng test
```

**Example Test:**
```typescript
describe('TaskPanelComponent', () => {
  let component: TaskPanelComponent;
  let fixture: ComponentFixture<TaskPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TaskPanelComponent ],
      imports: [ MarkdownModule.forRoot() ]
    }).compileComponents();
  });

  it('should display task description', () => {
    component.taskDescription = '# Test Task';
    fixture.detectChanges();
    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('h1').textContent).toContain('Test Task');
  });
});
```

### E2E Tests

```bash
ng e2e
```

---

## Environment Configuration

**File**: `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8888/api'
};
```

**Production**: `src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.yourdomain.com/api'
};
```

---

## Best Practices

1. **Component Design**:
   - Keep components focused and small
   - Use OnPush change detection for performance
   - Unsubscribe from observables in ngOnDestroy

2. **Service Usage**:
   - Use singleton services (`providedIn: 'root'`)
   - Handle errors in services, not components
   - Cache data when appropriate

3. **State Management**:
   - Use observables for async data
   - Avoid nested subscriptions (use operators like switchMap)
   - Share observable streams with shareReplay

4. **Performance**:
   - Lazy load routes
   - Use trackBy in *ngFor loops
   - Optimize bundle size with tree-shaking

5. **Accessibility**:
   - Use semantic HTML
   - Add ARIA labels
   - Ensure keyboard navigation

---

## Common Tasks

### Adding a New Component

```bash
ng generate component my-component
```

### Adding a New Service

```bash
ng generate service shared/services/my-service
```

### Adding a Route

```typescript
// In app-routing.module.ts
{
  path: 'my-route',
  component: MyComponent,
  canActivate: [AuthGuard]
}
```

### Making an API Call

```typescript
constructor(private http: HttpClient) {}

getData() {
  return this.http.get<DataType>(`${environment.apiUrl}/endpoint`);
}
```

---

## Troubleshooting

### Module Not Found

```bash
npm install
```

### Build Errors

```bash
rm -rf node_modules package-lock.json
npm install
ng build
```

### Monaco Editor Not Loading

Check that monaco-editor is properly installed and imported in angular.json.

---

## Resources

- [Angular Documentation](https://angular.io/docs)
- [Angular Material](https://material.angular.io/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [RxJS Documentation](https://rxjs.dev/)
