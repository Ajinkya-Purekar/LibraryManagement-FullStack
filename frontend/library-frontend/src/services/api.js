import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

/* ================= TOKEN INTERCEPTOR ================= */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ================= AUTH (❗UNCHANGED) ================= */
export const loginUser = (data) => {
  const formData = new URLSearchParams();
  formData.append("username", data.username);
  formData.append("password", data.password);

  return api.post("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
};

export const registerUser = (data) =>
  api.post("/auth/register", data);

/* ================= DASHBOARD ================= */
export const getAdminSummary = () =>
  api.get("/admin/dashboard/summary");

export const getUserDashboard = () =>
  api.get("/user/dashboard");

/* ================= BOOKS ================= */
export const getBooks = (
  search = "",
  categoryId = "",
  page = 1,
  size = 5,
  sortBy = "title",
  order = "asc"
) =>
  api.get("/books", {
    params: {
      search: search || undefined,
      category_id: categoryId || undefined,
      page,
      size,
      sort_by: sortBy,
      order,
    },
  });

export const addBook = (data) =>
  api.post("/books", data);

export const updateBook = (id, data) =>
  api.put(`/books/${id}`, data);

export const deleteBook = (id) =>
  api.delete(`/books/${id}`);

/* ================= CATEGORIES ================= */
export const getCategories = () =>
  api.get("/categories");

/* ================= ISSUE / RETURN (USER) ================= */
export const requestIssue = (bookId) =>
  api.post(`/issues/request-issue/${bookId}`);

export const requestReturn = (issueId) =>
  api.put(`/issues/request-return/${issueId}`);

export const getMyBooks = () =>
  api.get("/issues/my-books");

export const getMyHistory = () =>
  api.get("/issues/my-history");

/* ================= ISSUE / RETURN (ADMIN) ================= */
export const getPendingIssues = () =>
  api.get("/issues/admin/pending-issues");

export const getPendingReturns = () =>
  api.get("/issues/admin/pending-returns");

export const getOverdueBooks = () =>
  api.get("/issues/admin/overdue");

export const getAdminHistory = () =>
  api.get("/issues/admin/history");

export const approveIssue = (issueId) =>
  api.put(`/issues/admin/approve-issue/${issueId}`);

export const rejectIssue = (issueId) =>
  api.put(`/issues/admin/reject-issue/${issueId}`);

/*
  Backend approve-return DOES NOT expect body
*/
export const approveReturn = (issueId) =>
  api.put(`/issues/admin/approve-return/${issueId}`);

/*
  Backend reject-return expects:
  {
    "reason": "text"
  }
*/
export const rejectReturn = (issueId, reason) =>
  api.put(`/issues/admin/reject-return/${issueId}`, {
    reason,
  });

export default api;
