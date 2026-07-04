drop policy if exists user_settings_update_own on public.user_settings;
drop policy if exists user_settings_insert_own on public.user_settings;
drop policy if exists user_settings_select_own on public.user_settings;

drop policy if exists profiles_update_own on public.profiles;
drop policy if exists profiles_insert_own on public.profiles;
drop policy if exists profiles_select_own on public.profiles;

drop trigger if exists set_user_settings_updated_at on public.user_settings;
drop trigger if exists set_profiles_updated_at on public.profiles;
drop trigger if exists on_auth_user_created on auth.users;

drop function if exists public.handle_new_user();
drop function if exists public.set_updated_at();

drop index if exists public.user_settings_theme_idx;
drop index if exists public.profiles_role_idx;

drop table if exists public.user_settings;
drop table if exists public.profiles;
