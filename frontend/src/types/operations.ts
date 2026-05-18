export type OperationType = "RECEIPT" | "DELIVERY" | "INTERNAL" | "ADJUSTMENT";
export type OperationStatus = "DRAFT" | "CONFIRMED" | "DONE" | "CANCELLED";

export interface StockMoveRead {
  id: string;
  product_id: string;
  product_name: string;
  product_sku: string;
  product_uom: string;
  demand_qty: string;
  done_qty: string | null;
  src_location_id: string | null;
  src_location_name: string | null;
  dest_location_id: string | null;
  dest_location_name: string | null;
}

export interface Operation {
  id: string;
  reference: string;
  type: OperationType;
  status: OperationStatus;
  supplier: string | null;
  customer: string | null;
  supplier_id: string | null;
  customer_id: string | null;
  supplier_name: string | null;
  customer_name: string | null;
  supplier_address: string | null;
  customer_address: string | null;
  notes: string | null;
  src_location_id: string | null;
  src_location_name: string | null;
  dest_location_id: string | null;
  dest_location_name: string | null;
  scheduled_date: string | null;
  validated_at: string | null;
  created_by_name: string | null;
  created_at: string;
  moves: StockMoveRead[];
}

export interface OperationListItem {
  id: string;
  reference: string;
  type: OperationType;
  status: OperationStatus;
  supplier: string | null;
  customer: string | null;
  supplier_name: string | null;
  customer_name: string | null;
  supplier_address: string | null;
  customer_address: string | null;
  src_location_name: string | null;
  dest_location_name: string | null;
  scheduled_date: string | null;
  validated_at: string | null;
  created_at: string;
  move_count: number;
}

export interface LedgerEntry {
  id: string;
  product_id: string;
  product_name: string;
  product_sku: string;
  location_id: string;
  location_name: string;
  warehouse_name: string;
  operation_id: string | null;
  operation_reference: string | null;
  operation_type: OperationType | null;
  qty_change: string;
  balance_after: string;
  note: string | null;
  created_at: string;
}
