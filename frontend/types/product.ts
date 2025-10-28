export interface Product {
  id: string;
  name: string;
  description?: string;
  category?: string;
  price: number;
  stock?: number;
  discount?: number;
  status?: string;
  images?: string[];
  created_at?: string;
  updated_at?: string;
}
