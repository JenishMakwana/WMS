export interface Warehouse {
  id: string;
  name: string;
  short_code: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Location {
  id: string;
  name: string;
  short_code: string;
  warehouse_id: string;
  warehouse_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Supplier {
  id: string;
  name: string;
  contact_info: string | null;
  address: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  contact_info: string | null;
  address: string | null;
  is_active: boolean;
  created_at: string;
}

export interface StockByLocation {
  location_id: string;
  location_name: string;
  warehouse_name: string;
  quantity: string;
}

export interface Product {
  id: string;
  name: string;
  sku: string;
  description: string | null;
  unit_of_measure: string;
  category_id: string | null;
  category_name: string | null;
  is_active: boolean;
  total_stock: string;
  stock_by_location: StockByLocation[];
  created_at: string;
  updated_at: string | null;
}

export interface ProductListItem {
  id: string;
  name: string;
  sku: string;
  unit_of_measure: string;
  category_name: string | null;
  total_stock: string;
  is_active: boolean;
}
