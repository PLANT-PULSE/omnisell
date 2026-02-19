/**
 * OmniSell API Service
 * 
 * This file provides API service functions for the OmniSell frontend.
 * 
 * IMPORTANT: CORS Configuration
 * =============================
 * For this frontend to work with the backend, the backend MUST allow CORS requests
 * from "https://sellone.netlify.app/".
 * 
 * In the Django backend settings (sellflow/settings.py), ensure you have:
 * - django-cors-headers installed and added to INSTALLED_APPS
 * - CORS_ALLOWED_ORIGINS = ["https://sellone.netlify.app"]
 * - CORS_ALLOW_CREDENTIALS = True
 * 
 * =============================================================================
 * 
 * Backend URL Configuration
 * --------------------------
 * Change this variable to point to your backend API URL.
 * Currently configured for: https://omnisell-2.onrender.com
 */

const API_URL = 'https://omnisell-2.onrender.com';


/**
 * Utility function to handle API responses
 * @param {Response} response - Fetch API response object
 * @returns {Promise<any>} - Parsed JSON data
 * @throws {Error} - Throws error with message if request failed
 */
async function handleResponse(response) {
    // Clone the response so we can read it even if it fails
    const clonedResponse = response.clone();
    
    try {
        const data = await response.json();
        
        if (!response.ok) {
            // Handle different error status codes
            if (response.status === 401) {
                // Unauthorized -可能是token过期
                console.error('Authentication error: Token may be expired or invalid');
                throw new Error(data.detail || 'Authentication failed. Please login again.');
            } else if (response.status === 403) {
                console.error('Permission denied:', data);
                throw new Error(data.detail || 'You do not have permission to perform this action.');
            } else if (response.status === 404) {
                console.error('Resource not found:', data);
                throw new Error(data.detail || 'The requested resource was not found.');
            } else if (response.status >= 500) {
                console.error('Server error:', data);
                throw new Error('Server error. Please try again later.');
            } else {
                // Other client errors
                const errorMessage = data.detail || Object.values(data).flat().join(', ') || 'An error occurred';
                console.error('API Error:', errorMessage, data);
                throw new Error(errorMessage);
            }
        }
        
        return data;
    } catch (error) {
        if (error.name === 'SyntaxError') {
            // Response was not JSON
            if (!response.ok) {
                console.error('Non-JSON error response:', clonedResponse);
                throw new Error(`Request failed with status ${response.status}`);
            }
            return {};
        }
        throw error;
    }
}


/**
 * Get authentication token from localStorage
 * @returns {string|null} - JWT token or null
 */
function getAuthToken() {
    const userData = localStorage.getItem('sellflow_user');
    if (userData) {
        const parsed = JSON.parse(userData);
        return parsed.access || parsed.token || null;
    }
    return null;
}


/**
 * Get headers for authenticated requests
 * @returns {Object} - Headers object with Authorization header
 */
function getAuthHeaders() {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}


/**
 * Get headers for requests that may include file uploads
 * @returns {Object} - Headers object without Content-Type (for FormData)
 */
function getMultipartHeaders() {
    const token = getAuthToken();
    const headers = {};
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}


console.log(`OmniSell API Service initialized. Backend URL: ${API_URL}`);


// =============================================================================
// AUTHENTICATION API
// =============================================================================

/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User email
 * @param {string} userData.password - User password
 * @param {string} userData.password_confirm - Password confirmation
 * @param {string} userData.first_name - User first name
 * @param {string} userData.last_name - User last name
 * @param {string} [userData.phone] - User phone number
 * @returns {Promise<Object>} - Registration response
 */
async function registerUser(userData) {
    console.log('Attempting to register user:', userData.email);
    
    try {
        const response = await fetch(`${API_URL}/api/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify(userData),
        });
        
        const data = await handleResponse(response);
        console.log('Registration successful:', data);
        return data;
    } catch (error) {
        console.error('Registration failed:', error.message);
        throw error;
    }
}


/**
 * Login user
 * @param {Object} credentials - User login credentials
 * @param {string} credentials.email - User email
 * @param {string} credentials.password - User password
 * @returns {Promise<Object>} - Login response with tokens
 */
async function loginUser(credentials) {
    console.log('Attempting to login:', credentials.email);
    
    try {
        const response = await fetch(`${API_URL}/api/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify(credentials),
        });
        
        const data = await handleResponse(response);
        console.log('Login successful');
        
        // Store tokens in localStorage
        if (data.access && data.refresh) {
            const userData = JSON.parse(localStorage.getItem('sellflow_user') || '{}');
            userData.access = data.access;
            userData.refresh = data.refresh;
            userData.isLoggedIn = true;
            localStorage.setItem('sellflow_user', JSON.stringify(userData));
        }
        
        return data;
    } catch (error) {
        console.error('Login failed:', error.message);
        throw error;
    }
}


/**
 * Refresh authentication token
 * @param {string} refreshToken - Refresh token
 * @returns {Promise<Object>} - New token pair
 */
async function refreshToken(refreshToken) {
    console.log('Refreshing token...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        
        const data = await handleResponse(response);
        console.log('Token refreshed successfully');
        
        // Update stored tokens
        if (data.access) {
            const userData = JSON.parse(localStorage.getItem('sellflow_user') || '{}');
            userData.access = data.access;
            localStorage.setItem('sellflow_user', JSON.stringify(userData));
        }
        
        return data;
    } catch (error) {
        console.error('Token refresh failed:', error.message);
        // Clear auth data on refresh failure
        localStorage.removeItem('sellflow_user');
        throw error;
    }
}


/**
 * Verify if token is valid
 * @param {string} token - JWT token to verify
 * @returns {Promise<boolean>} - True if token is valid
 */
async function verifyToken(token) {
    try {
        const response = await fetch(`${API_URL}/api/auth/token/verify/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({ token: token }),
        });
        
        await handleResponse(response);
        return true;
    } catch (error) {
        console.error('Token verification failed:', error.message);
        return false;
    }
}


/**
 * Logout user (client-side)
 */
function logoutUser() {
    console.log('Logging out user');
    localStorage.removeItem('sellflow_user');
    window.location.reload();
}


// =============================================================================
// USER PROFILE API
// =============================================================================

/**
 * Get current user profile
 * Endpoint: GET /api/auth/profile/
 * @returns {Promise<Object>} - User profile data
 */
async function getUserProfile() {
    console.log('Fetching user profile...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/profile/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('User profile fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch user profile:', error.message);
        throw error;
    }
}


/**
 * Update user profile
 * Endpoint: PATCH /api/auth/profile/
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>} - Updated profile data
 */
async function updateUserProfile(profileData) {
    console.log('Updating user profile...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/profile/`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify(profileData),
        });
        
        const data = await handleResponse(response);
        console.log('Profile updated:', data);
        return data;
    } catch (error) {
        console.error('Failed to update profile:', error.message);
        throw error;
    }
}


/**
 * Get user details
 * Endpoint: GET /api/auth/user/
 * @returns {Promise<Object>} - User data
 */
async function getUserDetails() {
    console.log('Fetching user details...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/user/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('User details fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch user details:', error.message);
        throw error;
    }
}


/**
 * Get user activities
 * Endpoint: GET /api/auth/activities/
 * @returns {Promise<Array>} - User activities
 */
async function getUserActivities() {
    console.log('Fetching user activities...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/activities/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('User activities fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch activities:', error.message);
        throw error;
    }
}


// =============================================================================
// PRODUCTS API
// =============================================================================

/**
 * Get all products
 * @param {Object} [params] - Query parameters
 * @param {string} [params.search] - Search term
 * @param {number} [params.category] - Category ID
 * @param {number} [params.page] - Page number
 * @returns {Promise<Object>} - Products list with pagination
 */
async function getProducts(params = {}) {
    console.log('Fetching products...', params);
    
    try {
        const queryParams = new URLSearchParams();
        
        if (params.search) queryParams.append('search', params.search);
        if (params.category) queryParams.append('category', params.category);
        if (params.page) queryParams.append('page', params.page);
        
        const queryString = queryParams.toString();
        const url = `${API_URL}/api/products/${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Products fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch products:', error.message);
        throw error;
    }
}


/**
 * Get product by ID
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} - Product details
 */
async function getProductById(productId) {
    console.log('Fetching product:', productId);
    
    try {
        const response = await fetch(`${API_URL}/api/products/${productId}/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Product fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch product:', error.message);
        throw error;
    }
}


/**
 * Create a new product
 * @param {Object} productData - Product data
 * @returns {Promise<Object>} - Created product
 */
async function createProduct(productData) {
    console.log('Creating product...', productData.name);
    
    try {
        const response = await fetch(`${API_URL}/api/products/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(productData),
        });
        
        const data = await handleResponse(response);
        console.log('Product created:', data);
        return data;
    } catch (error) {
        console.error('Failed to create product:', error.message);
        throw error;
    }
}


/**
 * Update a product
 * @param {number} productId - Product ID
 * @param {Object} productData - Updated product data
 * @returns {Promise<Object>} - Updated product
 */
async function updateProduct(productId, productData) {
    console.log('Updating product:', productId);
    
    try {
        const response = await fetch(`${API_URL}/api/products/${productId}/`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify(productData),
        });
        
        const data = await handleResponse(response);
        console.log('Product updated:', data);
        return data;
    } catch (error) {
        console.error('Failed to update product:', error.message);
        throw error;
    }
}


/**
 * Delete a product
 * @param {number} productId - Product ID
 * @returns {Promise<void>}
 */
async function deleteProduct(productId) {
    console.log('Deleting product:', productId);
    
    try {
        const response = await fetch(`${API_URL}/api/products/${productId}/`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        
        await handleResponse(response);
        console.log('Product deleted successfully');
    } catch (error) {
        console.error('Failed to delete product:', error.message);
        throw error;
    }
}


/**
 * Upload product image
 * @param {number} productId - Product ID
 * @param {File} imageFile - Image file
 * @returns {Promise<Object>} - Uploaded image data
 */
async function uploadProductImage(productId, imageFile) {
    console.log('Uploading product image...');
    
    try {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        const response = await fetch(`${API_URL}/api/products/${productId}/upload_image/`, {
            method: 'POST',
            headers: getMultipartHeaders(),
            body: formData,
        });
        
        const data = await handleResponse(response);
        console.log('Image uploaded:', data);
        return data;
    } catch (error) {
        console.error('Failed to upload image:', error.message);
        throw error;
    }
}


/**
 * Get all categories
 * @returns {Promise<Array>} - Categories list
 */
async function getCategories() {
    console.log('Fetching categories...');
    
    try {
        const response = await fetch(`${API_URL}/api/products/categories/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Categories fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch categories:', error.message);
        throw error;
    }
}


/**
 * Get public products (for social media sharing)
 * @returns {Promise<Array>} - Public products list
 */
async function getPublicProducts() {
    console.log('Fetching public products...');
    
    try {
        const response = await fetch(`${API_URL}/api/products/public/list/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        const data = await handleResponse(response);
        console.log('Public products fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch public products:', error.message);
        throw error;
    }
}


// =============================================================================
// SOCIAL POSTS API
// =============================================================================

/**
 * Get social posts
 * @returns {Promise<Array>} - Social posts list
 */
async function getSocialPosts() {
    console.log('Fetching social posts...');
    
    try {
        const response = await fetch(`${API_URL}/api/products/posts/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Social posts fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch social posts:', error.message);
        throw error;
    }
}


/**
 * Create a social post
 * @param {Object} postData - Post data
 * @returns {Promise<Object>} - Created post
 */
async function createSocialPost(postData) {
    console.log('Creating social post...');
    
    try {
        const response = await fetch(`${API_URL}/api/products/posts/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(postData),
        });
        
        const data = await handleResponse(response);
        console.log('Social post created:', data);
        return data;
    } catch (error) {
        console.error('Failed to create social post:', error.message);
        throw error;
    }
}


// =============================================================================
// CART API
// =============================================================================

/**
 * Get cart items
 * @returns {Promise<Array>} - Cart items
 */
async function getCart() {
    console.log('Fetching cart...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/cart/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Cart fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch cart:', error.message);
        throw error;
    }
}


/**
 * Add item to cart
 * @param {number} productId - Product ID
 * @param {number} quantity - Quantity
 * @returns {Promise<Object>} - Cart response
 */
async function addToCart(productId, quantity = 1) {
    console.log('Adding to cart:', productId, 'qty:', quantity);
    
    try {
        const response = await fetch(`${API_URL}/api/orders/cart/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                product: productId,
                quantity: quantity,
            }),
        });
        
        const data = await handleResponse(response);
        console.log('Added to cart:', data);
        return data;
    } catch (error) {
        console.error('Failed to add to cart:', error.message);
        throw error;
    }
}


/**
 * Update cart item quantity
 * @param {number} itemId - Cart item ID
 * @param {number} quantity - New quantity
 * @returns {Promise<Object>} - Updated cart item
 */
async function updateCartItem(itemId, quantity) {
    console.log('Updating cart item:', itemId, 'qty:', quantity);
    
    try {
        const response = await fetch(`${API_URL}/api/orders/cart/${itemId}/`, {
            method: 'PATCH',
            headers: getAuthHeaders(),
            body: JSON.stringify({ quantity: quantity }),
        });
        
        const data = await handleResponse(response);
        console.log('Cart item updated:', data);
        return data;
    } catch (error) {
        console.error('Failed to update cart item:', error.message);
        throw error;
    }
}


/**
 * Remove item from cart
 * @param {number} itemId - Cart item ID
 * @returns {Promise<void>}
 */
async function removeFromCart(itemId) {
    console.log('Removing from cart:', itemId);
    
    try {
        const response = await fetch(`${API_URL}/api/orders/cart/${itemId}/`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        
        await handleResponse(response);
        console.log('Item removed from cart');
    } catch (error) {
        console.error('Failed to remove from cart:', error.message);
        throw error;
    }
}


/**
 * Clear cart
 * @returns {Promise<void>}
 */
async function clearCart() {
    console.log('Clearing cart...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/cart/clear/`, {
            method: 'POST',
            headers: getAuthHeaders(),
        });
        
        await handleResponse(response);
        console.log('Cart cleared');
    } catch (error) {
        console.error('Failed to clear cart:', error.message);
        throw error;
    }
}


// =============================================================================
// ORDERS API
// =============================================================================

/**
 * Get user orders
 * @returns {Promise<Array>} - Orders list
 */
async function getOrders() {
    console.log('Fetching orders...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/orders/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Orders fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch orders:', error.message);
        throw error;
    }
}


/**
 * Get order by ID
 * @param {number} orderId - Order ID
 * @returns {Promise<Object>} - Order details
 */
async function getOrderById(orderId) {
    console.log('Fetching order:', orderId);
    
    try {
        const response = await fetch(`${API_URL}/api/orders/orders/${orderId}/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Order fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch order:', error.message);
        throw error;
    }
}


/**
 * Create order from cart (checkout)
 * @param {Object} checkoutData - Checkout data
 * @returns {Promise<Object>} - Created order
 */
async function createOrder(checkoutData) {
    console.log('Creating order...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/checkout/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(checkoutData),
        });
        
        const data = await handleResponse(response);
        console.log('Order created:', data);
        return data;
    } catch (error) {
        console.error('Failed to create order:', error.message);
        throw error;
    }
}


/**
 * Get public order by UUID (for social media sharing)
 * @param {string} orderUuid - Order UUID
 * @returns {Promise<Object>} - Public order details
 */
async function getPublicOrder(orderUuid) {
    console.log('Fetching public order:', orderUuid);
    
    try {
        const response = await fetch(`${API_URL}/api/orders/public/order/${orderUuid}/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });
        
        const data = await handleResponse(response);
        console.log('Public order fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch public order:', error.message);
        throw error;
    }
}


// =============================================================================
// PAYMENTS API
// =============================================================================

/**
 * Get payment methods
 * @returns {Promise<Array>} - Payment methods
 */
async function getPaymentMethods() {
    console.log('Fetching payment methods...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/payments/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Payment methods fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch payment methods:', error.message);
        throw error;
    }
}


/**
 * Process payment
 * @param {Object} paymentData - Payment data
 * @returns {Promise<Object>} - Payment result
 */
async function processPayment(paymentData) {
    console.log('Processing payment...');
    
    try {
        const response = await fetch(`${API_URL}/api/orders/payments/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(paymentData),
        });
        
        const data = await handleResponse(response);
        console.log('Payment processed:', data);
        return data;
    } catch (error) {
        console.error('Failed to process payment:', error.message);
        throw error;
    }
}


// =============================================================================
// NOTIFICATIONS API
// =============================================================================

/**
 * Get notifications
 * @returns {Promise<Array>} - Notifications list
 */
async function getNotifications() {
    console.log('Fetching notifications...');
    
    try {
        const response = await fetch(`${API_URL}/api/notifications/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Notifications fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch notifications:', error.message);
        throw error;
    }
}


/**
 * Mark notification as read
 * @param {number} notificationId - Notification ID
 * @returns {Promise<void>}
 */
async function markNotificationRead(notificationId) {
    console.log('Marking notification as read:', notificationId);
    
    try {
        const response = await fetch(`${API_URL}/api/notifications/${notificationId}/read/`, {
            method: 'POST',
            headers: getAuthHeaders(),
        });
        
        await handleResponse(response);
        console.log('Notification marked as read');
    } catch (error) {
        console.error('Failed to mark notification as read:', error.message);
        throw error;
    }
}


// =============================================================================
// ANALYTICS API
// =============================================================================

/**
 * Get sales analytics
 * Endpoint: GET /api/analytics/
 * @param {Object} [params] - Query parameters
 * @param {string} [params.period] - Period (day, week, month, year)
 * @returns {Promise<Object>} - Analytics data
 */
async function getAnalytics(params = {}) {
    console.log('Fetching analytics...', params);
    
    try {
        const queryParams = new URLSearchParams();
        if (params.period) queryParams.append('period', params.period);
        
        const queryString = queryParams.toString();
        const url = `${API_URL}/api/analytics/${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Analytics fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch analytics:', error.message);
        throw error;
    }
}


// =============================================================================
// CHAT / MESSAGING API
// =============================================================================

/**
 * Get conversations
 * @returns {Promise<Array>} - Conversations list
 */
async function getConversations() {
    console.log('Fetching conversations...');
    
    try {
        const response = await fetch(`${API_URL}/api/chat/conversations/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Conversations fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch conversations:', error.message);
        throw error;
    }
}


/**
 * Get messages in a conversation
 * @param {number} conversationId - Conversation ID
 * @returns {Promise<Array>} - Messages list
 */
async function getMessages(conversationId) {
    console.log('Fetching messages for conversation:', conversationId);
    
    try {
        const response = await fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Messages fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch messages:', error.message);
        throw error;
    }
}


/**
 * Send a message
 * @param {number} conversationId - Conversation ID
 * @param {string} message - Message text
 * @returns {Promise<Object>} - Sent message
 */
async function sendMessage(conversationId, message) {
    console.log('Sending message to conversation:', conversationId);
    
    try {
        const response = await fetch(`${API_URL}/api/chat/conversations/${conversationId}/messages/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ message: message }),
        });
        
        const data = await handleResponse(response);
        console.log('Message sent:', data);
        return data;
    } catch (error) {
        console.error('Failed to send message:', error.message);
        throw error;
    }
}


// =============================================================================
// AI SERVICES API
// =============================================================================

/**
 * Generate content using AI
 * Endpoint: POST /api/ai/generate/
 * @param {Object} data - Data for AI generation (type, product_data, etc.)
 * @returns {Promise<Object>} - Generated content
 */
async function generateContent(data) {
    console.log('Generating AI content...');
    
    try {
        const response = await fetch(`${API_URL}/api/ai/generate/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data),
        });
        
        const result = await handleResponse(response);
        console.log('AI content generated:', result);
        return result;
    } catch (error) {
        console.error('Failed to generate AI content:', error.message);
        throw error;
    }
}


/**
 * Generate product description using AI
 * @param {Object} data - Product data for description generation
 * @returns {Promise<Object>} - Generated description
 */
async function generateProductDescription(data) {
    console.log('Generating product description...');
    
    try {
        const response = await fetch(`${API_URL}/api/ai/generate/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                type: 'product_description',
                ...data
            }),
        });
        
        const result = await handleResponse(response);
        console.log('Description generated:', result);
        return result;
    } catch (error) {
        console.error('Failed to generate description:', error.message);
        throw error;
    }
}


/**
 * Generate social media post using AI
 * @param {Object} data - Product/Post data
 * @returns {Promise<Object>} - Generated post
 */
async function generateSocialPost(data) {
    console.log('Generating social post...');
    
    try {
        const response = await fetch(`${API_URL}/api/ai/generate/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                type: 'social_post',
                ...data
            }),
        });
        
        const result = await handleResponse(response);
        console.log('Social post generated:', result);
        return result;
    } catch (error) {
        console.error('Failed to generate social post:', error.message);
        throw error;
    }
}


/**
 * Chat with AI assistant
 * Endpoint: POST /api/ai/chat/
 * @param {string} message - User message
 * @param {string} [conversationId] - Optional conversation ID
 * @returns {Promise<Object>} - AI response
 */
async function chatWithAI(message, conversationId = null) {
    console.log('Chatting with AI...');
    
    try {
        const response = await fetch(`${API_URL}/api/ai/chat/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            }),
        });
        
        const result = await handleResponse(response);
        console.log('AI chat response:', result);
        return result;
    } catch (error) {
        console.error('Failed to chat with AI:', error.message);
        throw error;
    }
}


/**
 * Analyze product performance
 * Endpoint: GET /api/analytics/{id}/
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} - Performance analysis
 */
async function analyzeProductPerformance(productId) {
    console.log('Analyzing product performance:', productId);
    
    try {
        const response = await fetch(`${API_URL}/api/analytics/${productId}/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const result = await handleResponse(response);
        console.log('Product analysis:', result);
        return result;
    } catch (error) {
        console.error('Failed to analyze product:', error.message);
        throw error;
    }
}


// =============================================================================
// SOCIAL MEDIA CONNECTIONS API
// =============================================================================

/**
 * Get connected platforms
 * Endpoint: GET /api/auth/platforms/
 * @returns {Promise<Array>} - Connected platforms
 */
async function getConnectedPlatforms() {
    console.log('Fetching connected platforms...');
    
    try {
        const response = await fetch(`${API_URL}/api/auth/platforms/`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });
        
        const data = await handleResponse(response);
        console.log('Connected platforms fetched:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch platforms:', error.message);
        throw error;
    }
}


/**
 * Connect a social platform
 * Endpoint: POST /api/auth/platforms/
 * @param {string} platform - Platform name (facebook, instagram, tiktok, twitter)
 * @param {string} authToken - OAuth or access token
 * @returns {Promise<Object>} - Connection result
 */
async function connectPlatform(platform, authToken) {
    console.log('Connecting platform:', platform);
    
    try {
        const response = await fetch(`${API_URL}/api/auth/platforms/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                platform: platform,
                auth_token: authToken,
            }),
        });
        
        const data = await handleResponse(response);
        console.log('Platform connected:', data);
        return data;
    } catch (error) {
        console.error('Failed to connect platform:', error.message);
        throw error;
    }
}


/**
 * Disconnect a social platform
 * Endpoint: DELETE /api/auth/platforms/{id}/
 * @param {number} platformId - Platform connection ID
 * @returns {Promise<void>}
 */
async function disconnectPlatform(platformId) {
    console.log('Disconnecting platform:', platformId);
    
    try {
        const response = await fetch(`${API_URL}/api/auth/platforms/${platformId}/`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        
        await handleResponse(response);
        console.log('Platform disconnected');
    } catch (error) {
        console.error('Failed to disconnect platform:', error.message);
        throw error;
    }
}


// =============================================================================
// EXPORT API SERVICE
// =============================================================================

// Create and export the API service object for easier importing
const apiService = {
    // Authentication
    registerUser,
    loginUser,
    logoutUser,
    refreshToken,
    verifyToken,
    
    // User Profile
    getUserProfile,
    updateUserProfile,
    getUserDetails,
    getUserActivities,
    
    // Products
    getProducts,
    getProductById,
    createProduct,
    updateProduct,
    deleteProduct,
    uploadProductImage,
    getCategories,
    getPublicProducts,
    
    // Social Posts
    getSocialPosts,
    createSocialPost,
    
    // Cart
    getCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    
    // Orders
    getOrders,
    getOrderById,
    createOrder,
    getPublicOrder,
    
    // Payments
    getPaymentMethods,
    processPayment,
    
    // Notifications
    getNotifications,
    markNotificationRead,
    
    // Analytics
    getAnalytics,
    analyzeProductPerformance,
    
    // Chat
    getConversations,
    getMessages,
    sendMessage,
    
    // AI Services
    generateContent,
    generateProductDescription,
    generateSocialPost,
    chatWithAI,
    
    // Social Connections
    getConnectedPlatforms,
    connectPlatform,
    disconnectPlatform,
    
    // Utility
    getAuthToken,
    getAuthHeaders,
    handleResponse,
    
    // Config
    API_URL,
};

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = apiService;
} else if (typeof window !== 'undefined') {
    window.apiService = apiService;
    // Also export individual functions to window for global access
    Object.keys(apiService).forEach(key => {
        window[key] = apiService[key];
    });
}
