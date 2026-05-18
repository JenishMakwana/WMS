export interface DashboardKPIs {
  total_products: number;
  total_stock_value: string;
  out_of_stock_count: number;
  pending_receipts: number;
  pending_deliveries: number;
  internal_transfers_scheduled: number;
  receipts_today: number;
  deliveries_today: number;
}

import type { OperationStatus, OperationType } from "./operations";

export interface RecentActivity {
  operation_id: string;
  reference: string;
  type: OperationType;
  status: OperationStatus;
  party: string | null;
  move_count: number;
  created_at: string;
}


export interface StockAlertItem {
  product_id: string;
  product_name: string;
  sku: string;
  unit_of_measure: string;
  total_stock: string;
  is_out_of_stock: boolean;
}
