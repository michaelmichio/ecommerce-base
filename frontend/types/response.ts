import { Product } from "./product";

export interface ProductListResponse {
  success: boolean;
  data: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    items: Product[];
  };
}
