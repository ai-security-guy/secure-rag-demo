import { Routes, Router } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home';
import { inject } from '@angular/core';
import { Auth, user } from '@angular/fire/auth';
import { map } from 'rxjs/operators';

// Simple Auth Guard
const authGuard = () => {
  const auth = inject(Auth);
  return user(auth).pipe(map(u => !!u || inject(Router).createUrlTree(['/login'])));
};

export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent }, // Add Auth Guard later if needed
  // Keep upload for direct access if wanted, or remove if integrated into Home
  { path: 'upload', loadComponent: () => import('./upload/upload').then(m => m.UploadComponent) }
];
