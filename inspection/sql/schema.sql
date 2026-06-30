// Unified Infrastructure Asset & Assessment Schema
// Designed to handle Bridge Inventory, Culvert Inventory, and Culvert Inspections simultaneously.

enum asset_type_enum {
  Bridge
  Culvert
}

enum assessment_type_enum {
  Inventory
  Condition
}

Table assets {
  id serial [pk]
  structure_number varchar [unique, not null, note: "Unique engineering ID across all structures"]
  structure_name varchar [not null]
  asset_type asset_type_enum [not null, note: "Distinguishes Bridge vs Culvert"]
  size_category varchar [note: "small, medium, large"]
  structure_orientation varchar [note: "skew, square"]
  angle_of_skew integer
  year_constructed integer
  
  // Geospatial & Location Data (Shared across all forms)
  latitude numeric
  longitude numeric
  road_number varchar
  road_km_chainage varchar
  maintenance_region varchar
  feature_crossed varchar
  feature_name varchar
  
  // Dynamic Asset Specifications
  // Bridges: max_pier_height, max_abutment_height, road_over_under
  // Culverts: max_fill_height, max_cell_width, min_cell_height
  inventory_specs jsonb [note: "Stores flexible component parameters as JSON schema object"]
}

Table assessments {
  id serial [pk]
  asset_id integer [ref: > assets.id, note: "Links directly to parent physical asset"]
  assessment_type assessment_type_enum [not null, note: "Inventory log vs Condition evaluation"]
  date_assessed timestamp [default: `now()`]
  inspector_name varchar
  inspector_firm varchar
  pci_score integer [note: "Condition assessment rating (0-100) or baseline score"]
  inspector_comments text
  
  // Shared Geometric Clearance parameters
  min_vertical_clearance_value numeric
  min_vertical_clearance_position varchar [note: "AS, S1, S2, etc."]
  
  // Dynamic Form Metadata 
  // Captures unique checklist items like expansion joint flags (has_expansion_joint_as, etc.)
  assessment_metadata jsonb [note: "Stores structural enums/checkbox variations across forms"]
}

Table asset_components {
  id serial [pk]
  asset_id integer [ref: > assets.id]
  component_label varchar [not null, note: "e.g., 'Cell 1', 'Span S1', 'Cell Length Component'"]
  width numeric [note: "Measured clearance or cell width"]
  length numeric [note: "Measured length attribute"]
}

Table condition_ratings {
  id serial [pk]
  assessment_id integer [ref: > assessments.id]
  item_number varchar [not null, note: "Form indicators like '01', '05', '10'"]
  item_name varchar [not null, note: "e.g., 'Apron Slabs', 'Walls', 'Waterway'"]
  position_code varchar [note: "Captures 'E1', 'E2', 'Cell 1' or NULL for single items"]
  degree integer [note: "0 to 4 scale rating"]
  extent integer [note: "1 to 4 scale rating"]
  relevancy integer [note: "1 to 4 scale rating"]
}

Table remedial_actions {
  id serial [pk]
  assessment_id integer [ref: > assessments.id]
  item_number varchar
  inspection_item varchar
  position varchar
  activity_description text
  quantity numeric
  unit varchar
  urgency varchar
  make_safe boolean [default: false]
  remarks text
}

Table media_attachments {
  id serial [pk]
  assessment_id integer [ref: > assessments.id]
  remedial_action_id integer [ref: > remedial_actions.id, null]
  perspective_label varchar [note: "e.g., 'Side View', 'Inlet View', 'Defect Photo'"]
  photo_link varchar [not null, note: "URL path mapping to your application media bucket"]
  uploaded_at timestamp [default: `now()`]
}