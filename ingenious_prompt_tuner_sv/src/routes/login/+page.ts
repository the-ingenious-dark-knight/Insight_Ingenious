import { onMount } from 'svelte';
import { writable } from 'svelte/store';
import { _get_token, _set_token } from '../../lib/stores';


export let _username: string = '';
export let _password: string = '';
export let _error: string | null = null;
export let _token = writable<string | null>(null);


export async function _login() {
    try {
        const response = await fetch('http://localhost:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'username': _username,
                'password': _password
            })
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        _set_token(window, data.access_token);        
    } catch (err) {
        _error = (err as Error).message;
    }
}