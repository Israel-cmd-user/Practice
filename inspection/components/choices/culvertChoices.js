/**
*@typedef {Object} MaintenanceItem
*@property {string} id
*@property {string} label
*@type {Object.<string, MaintenanceItem[]>}
*/

/**
 * @type {Object.<string, MaintenanceItem[]>}
 */

export const SIZE_CATEGORY_CUL = [
    {id: 1, label: "Small Major Culvert (shorter than 5m) "},
    {id: 2, label: "Large Major Culvert (Longer than 10m"}
];

export const CULVERT_TYPE = [
    {id: 1, label: "Simply suported" },
    {id: 2, label: "Continuous"},
    {id: 3, label: "Cantilever with drops in spans"},
    {id: 4, label: "Frame"},
    {id: 5, label: "Arch"},
    {id: 6, label: "Cable"},
    {id: 7, label: "Truss"},
    {id: 8, label: "Plate girder"},
    {id: 9, label: "Cellular"},
    {id: 10, label: "Continous and simply supported"},
    {id: 11, label: "Corrugated metal arch"},
    {id: 12, label: "Multi-continuous"},
    {id: 13, label: "Integral bridge"},
    {id: 14, label: "Continuous with drop-in span"},
    {id: 15, label: "NA"},
    {id: 16, label: "Unknown"},
    {id: 17 , labl: "Other"}
];

export const MAINTENANCE_TASKS = {
  "ApronSlabs": [
    { id: "01.001", label: "Apply protective coating" },
    { id: "01.002", label: "Apply bitumen" },
    { id: "01.003", label: "Concrete (pour/cured)" },
    { id: "01.004", label: "Concrete (repair)" },
    { id: "01.005", label: "Cut back reinforcement (bar ends and coatings)" },
    { id: "01.006", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "01.007", label: "Seal cracks" },
    { id: "01.008", label: "Earth backfill" },
    { id: "01.009", label: "Grouting (maintenance and fixings)" },
    { id: "01.010", label: "New concrete to drill" },
    { id: "01.011", label: "Rock backfill" },
    { id: "01.012", label: "Clear debris" },
    { id: "01.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "WingRetHeadWalls": [
    { id: "02.001", label: "Apply protective coating" },
    { id: "02.002", label: "Apply bitumen" },
    { id: "02.003", label: "Clean concrete surface" },
    { id: "02.004", label: "Concrete (pour/cured)" },
    { id: "02.005", label: "Concrete (repair)" },
    { id: "02.006", label: "Cut back reinforcement (bar ends and coatings)" },
    { id: "02.007", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "02.008", label: "Seal cracks" },
    { id: "02.009", label: "Stabilise wall with ground/rock anchors" },
    { id: "02.010", label: "Earth backfill" },
    { id: "02.011", label: "Grouting (maintenance and fixings)" },
    { id: "02.012", label: "New concrete to drill" },
    { id: "02.013", label: "Rock backfill" },
    { id: "02.014", label: "Waterproofing (inject cavity water barrier)" },
    { id: "02.015", label: "Clear debris" },
    { id: "02.016", label: "Repair weep holes" },
    { id: "02.017", label: "Monitor (movements, rotations, etc.) (1 year period)" },
    { id: "02.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "ScourProtectionWorks": [
    { id: "03.001", label: "Concrete (pour/cured)" },
    { id: "03.002", label: "Concrete (repair)" },
    { id: "03.003", label: "Grouting (maintenance and fixings)" },
    { id: "03.004", label: "New concrete to drill" },
    { id: "03.005", label: "Rock backfill" },
    { id: "03.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "Embankments": [
    { id: "04.001", label: "Repair concrete surface (spalling/cracks/etc)" },
    { id: "04.002", label: "Earth backfill" },
    { id: "04.003", label: "Grouting (maintenance and fixings)" },
    { id: "04.004", label: "New concrete to drill" },
    { id: "04.005", label: "Rock backfill" },
    { id: "04.006", label: "Clear debris" },
    { id: "04.007", label: "Interlocking blocks" },
    { id: "04.008", label: "Geotextile underlayer structure" },
    { id: "04.009", label: "Replace individual armour" },
    { id: "04.010", label: "Replace mass fill/core list" },
    { id: "04.011", label: "Replace retaining/underpinning structure" },
    { id: "04.012", label: "Replace wing/toe wall structure" },
    { id: "04.013", label: "Small maritime repairs" },
    { id: "04.014", label: "Apply weed killer, clearance and remove growth" },
    { id: "04.015", label: "Clear brush" },
    { id: "04.016", label: "Remove trees up to 300mm" },
    { id: "04.017", label: "Remove trees over 300mm" },
    { id: "04.018", label: "Remove structures (asphalt/fill)" },
    { id: "04.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "Waterway": [
    { id: "05.001", label: "Earth fill surface damage (earth)" },
    { id: "05.002", label: "Earth fill surface damage (chips/stone)" },
    { id: "05.003", label: "Earth fill surface damage (rock)" },
    { id: "05.004", label: "Grouting (maintenance and fixings)" },
    { id: "05.005", label: "Clear debris" },
    { id: "05.006", label: "Clear vegetation" },
    { id: "05.007", label: "Remove trees up to 300mm" },
    { id: "05.008", label: "Remove trees over 300mm" },
    { id: "05.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "RoadSlabs": [
    { id: "06.001", label: "Apply protective coating" },
    { id: "06.002", label: "Apply bitumen" },
    { id: "06.003", label: "Concrete (pour/cured)" },
    { id: "06.004", label: "Concrete (repair)" },
    { id: "06.005", label: "Repair concrete topping" },
    { id: "06.006", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "06.007", label: "Seal cracks" },
    { id: "06.008", label: "Earth backfill" },
    { id: "06.009", label: "New concrete to drill" },
    { id: "06.010", label: "Rock backfill" },
    { id: "06.011", label: "Clear debris" },
    { id: "06.012", label: "Crack and seat pavement" },
    { id: "06.013", label: "Resurface asphalt or pitch" },
    { id: "06.014", label: "Traffic accommodations minor (< 100 vpd)" },
    { id: "06.015", label: "Traffic accommodations medium (1000 - 10,000 vpd)" },
    { id: "06.016", label: "Traffic accommodations major (> 10,000 vpd)" },
    { id: "06.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "RoadJoints": [
    { id: "07.001", label: "Clear debris" },
    { id: "07.002", label: "Install signs / signs renewal" },
    { id: "07.003", label: "Paint over plates / replacements" },
    { id: "07.004", label: "Monitor (movements, rotations, etc.) (1 year period)" },
    { id: "07.005", label: "New movement joint" },
    { id: "07.006", label: "New asphalt plug joint" },
    { id: "07.007", label: "Refurbish (paint, strip, metal finishes)" },
    { id: "07.008", label: "Repair concrete of post system" },
    { id: "07.009", label: "Replace gland of close joint" },
    { id: "07.010", label: "Replace panel / seal with silicone" },
    { id: "07.011", label: "Solid silicone plugs" },
    { id: "07.012", label: "Traffic accommodations minor (< 100 vpd)" },
    { id: "07.013", label: "Traffic accommodations medium (1000 - 10,000 vpd)" },
    { id: "07.014", label: "Traffic accommodations major (> 10,000 vpd)" },
    { id: "07.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "Guardrails": [
    { id: "08.001", label: "Alter height of guard rails" },
    { id: "08.002", label: "Cat walks/protective safety" },
    { id: "08.003", label: "New guardrail (single and double)" },
    { id: "08.004", label: "Repair guardrail (posts, bolts, replacement etc)" },
    { id: "08.005", label: "Replace bolts and washers" },
    { id: "08.006", label: "Replace panel (steel or timber)" },
    { id: "08.007", label: "Replace reflector" },
    { id: "08.008", label: "Tension tops of guardrails" },
    { id: "08.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "ParapetsHandrails": [
    { id: "09.001", label: "Apply protective coating" },
    { id: "09.002", label: "Apply bitumen" },
    { id: "09.003", label: "Clean concrete surface" },
    { id: "09.004", label: "Concrete (pour/cured)" },
    { id: "09.005", label: "New anchors" },
    { id: "09.006", label: "New handrails (steel)" },
    { id: "09.007", label: "Seal cracks" },
    { id: "09.008", label: "Replace post system" },
    { id: "09.009", label: "Install full height pedestrian balustrade" },
    { id: "09.010", label: "Open protective parapet" },
    { id: "09.011", label: "Open traffic barriers (containment/apron)" },
    { id: "09.012", label: "Provide parapet coating" },
    { id: "09.013", label: "Connected rails" },
    { id: "09.014", label: "Re-align handrails" },
    { id: "09.015", label: "Replace panels, vertical fixings" },
    { id: "09.016", label: "Replace posts and baseplates" },
    { id: "09.017", label: "Replace bolts and washers" },
    { id: "09.018", label: "Replace vertical clearances" },
    { id: "09.019", label: "Screen panels hanging from barrier surface" },
    { id: "09.020", label: "Traffic accommodations minor (< 100 vpd)" },
    { id: "09.021", label: "Traffic accommodations medium (1000 - 10,000 vpd)" },
    { id: "09.022", label: "Traffic accommodations major (> 10,000 vpd)" },
    { id: "09.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "Walls": [
    { id: "10.001", label: "Apply protective coating" },
    { id: "10.002", label: "Apply bitumen" },
    { id: "10.003", label: "Clean concrete surface" },
    { id: "10.004", label: "Concrete (pour/cured)" },
    { id: "10.005", label: "Concrete (repair)" },
    { id: "10.006", label: "Cut back reinforcement (bar ends and coatings)" },
    { id: "10.007", label: "Repair anchor heads" },
    { id: "10.008", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "10.009", label: "Seal cracks" },
    { id: "10.010", label: "Stabilise wall with ground/rock anchors" },
    { id: "10.011", label: "Replace bearing pad" },
    { id: "10.012", label: "Target survey bodies" },
    { id: "10.013", label: "Survey using scaffold (< 10 m)" }
  ],
  "TopSlab": [
    { id: "11.001", label: "Apply protective coating" },
    { id: "11.002", label: "Apply bitumen" },
    { id: "11.003", label: "Clean concrete surface" },
    { id: "11.004", label: "Concrete (pour/cured)" },
    { id: "11.005", label: "Cut back reinforcement (bar ends and coatings)" },
    { id: "11.006", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "11.007", label: "Seal cracks" },
    { id: "11.008", label: "Hydrodemolition (peeling plates, carbon fiber, etc)" },
    { id: "11.009", label: "Spall damage repair" },
    { id: "11.010", label: "Survey using scaffold (< 10 m)" },
    { id: "11.011", label: "Traffic accommodations minor (< 100 vpd)" },
    { id: "11.012", label: "Traffic accommodations medium (1000 - 10,000 vpd)" },
    { id: "11.013", label: "Traffic accommodations major (> 10,000 vpd)" },
    { id: "11.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "InvertSlab": [
    { id: "12.001", label: "Apply protective coating" },
    { id: "12.002", label: "Apply bitumen" },
    { id: "12.003", label: "Concrete (pour/cured)" },
    { id: "12.004", label: "Concrete (repair)" },
    { id: "12.005", label: "Repair concrete topping" },
    { id: "12.006", label: "Repair spall (incl. fixing honeycombing)" },
    { id: "12.007", label: "Seal cracks" },
    { id: "12.008", label: "Earth backfill" },
    { id: "12.009", label: "New concrete to drill" },
    { id: "12.010", label: "Rock backfill" },
    { id: "12.011", label: "Clear debris" },
    { id: "12.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "CellDeformation": [
    { id: "13.001", label: "Concrete (pour/cured)" },
    { id: "13.002", label: "Concrete (repair)" },
    { id: "13.003", label: "Demolish and reconstruct" },
    { id: "13.004", label: "Stabilise wall using ground/rock anchors" },
    { id: "13.005", label: "Traffic accommodations minor (< 100 vpd)" },
    { id: "13.006", label: "Traffic accommodations medium (1000 - 10,000 vpd)" },
    { id: "13.007", label: "Traffic accommodations major (> 10,000 vpd)" },
    { id: "13.100", label: "Ad-hoc item (describe under remarks)" }
  ],
  "MiscellaneousItems": [
    { id: "14.001", label: "Replace cover plates and steel plates" },
    { id: "14.002", label: "Partial demolish road" },
    { id: "14.003", label: "Install clearance sign" },
    { id: "14.004", label: "Install markers" },
    { id: "14.005", label: "Install fencing" },
    { id: "14.006", label: "Remove post/fixing/structure to release" },
    { id: "14.007", label: "Replace road signs" },
    { id: "14.008", label: "Service structural hinge" },
    { id: "14.009", label: "Small structural steel works" },
    { id: "14.010", label: "Construct pedestal for culvert overlay" },
    { id: "14.100", label: "Ad-hoc item (describe under remarks)" }
  ]
};