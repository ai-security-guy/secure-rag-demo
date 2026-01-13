import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { Auth, signInWithEmailAndPassword, signOut, user, UserCredential } from '@angular/fire/auth';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule
  ],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <mat-card-header>
          <mat-card-title>Secure RAG Demo</mat-card-title>
          <mat-card-subtitle>Login to continue</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div *ngIf="user$ | async as user; else loginForm">
            <p>Welcome, {{ user.email }}!</p>
            <button mat-raised-button color="warn" (click)="logout()">Logout</button>
          </div>
          <ng-template #loginForm>
            <form (ngSubmit)="login()" class="login-form">
              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Email</mat-label>
                <input matInput type="email" [(ngModel)]="email" name="email" required>
              </mat-form-field>

              <mat-form-field appearance="fill" class="full-width">
                <mat-label>Password</mat-label>
                <input matInput type="password" [(ngModel)]="password" name="password" required>
              </mat-form-field>

              <div class="error-message" *ngIf="errorMessage">
                {{ errorMessage }}
              </div>

              <button mat-raised-button color="primary" type="submit" [disabled]="!email || !password">
                Login
              </button>
            </form>
          </ng-template>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .login-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background-color: #f0f2f5;
    }
    .login-card {
      width: 400px;
      text-align: center;
      padding: 24px;
    }
    .login-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-top: 16px;
    }
    .full-width {
      width: 100%;
    }
    mat-card-header {
      justify-content: center;
      margin-bottom: 8px;
    }
    .error-message {
      color: #f44336;
      font-size: 14px;
      margin-bottom: 8px;
    }
    button {
      width: 100%;
    }
  `]
})
export class LoginComponent {
  private auth: Auth = inject(Auth);
  private router: Router = inject(Router);
  user$ = user(this.auth);

  email = '';
  password = '';
  errorMessage = '';

  async login() {
    this.errorMessage = '';
    try {
      await signInWithEmailAndPassword(this.auth, this.email, this.password);
      this.router.navigate(['/home']);
    } catch (error: any) {
      console.error('Login failed', error);
      this.errorMessage = this.getErrorMessage(error);
    }
  }

  async logout() {
    await signOut(this.auth);
  }

  private getErrorMessage(error: any): string {
    switch (error.code) {
      case 'auth/invalid-email':
        return 'Invalid email format.';
      case 'auth/user-disabled':
        return 'This user has been disabled.';
      case 'auth/user-not-found':
        return 'User not found.';
      case 'auth/wrong-password':
        return 'Incorrect password.';
      case 'auth/invalid-credential':
        return 'Invalid credentials.';
      default:
        return 'Login failed. Please try again.';
    }
  }
}
