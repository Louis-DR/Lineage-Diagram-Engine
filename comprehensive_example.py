from lineage_diagram.diagram import Diagram
from lineage_diagram.lineage import Lineage
from lineage_diagram.bundle  import Bundle
from lineage_diagram.orbit   import Orbit

diagram = Diagram(view_width=2000, view_height=1250, resolution=1000)

color_blue        = 'steelblue'
color_red         = 'indianred'
color_green       = 'darkseagreen'
color_dark_green  = 'seagreen'
color_yellow      = 'goldenrod'
color_dark_yellow = 'darkgoldenrod'
color_white       = 'white'





# -----------------------------------------------------------------------------
# 1. Successive Transformations
# -----------------------------------------------------------------------------

line_successive = Lineage(
    diagram = diagram,
    color   = color_blue,
    start_x = 0,
    start_y = 100,
    start_w = 5
)
line_successive.scale_to(from_x= 100, to_x= 299, to_w=10)
line_successive.scale_to(from_x= 300, to_x= 499, to_w=40)
line_successive.shift_to(from_x= 500, to_x= 699, to_y=50)
line_successive.shift_to(from_x= 700, to_x= 899, to_y=100)
line_successive.scale_to(from_x=1100, to_x=1199, to_w=10)
line_successive.scale_to(from_x=1200, to_x=1299, to_w=40)
line_successive.shift_to(from_x=1300, to_x=1399, to_y=50)
line_successive.shift_to(from_x=1400, to_x=1499, to_y=100)
line_successive.scale_to(from_x=1500, to_x=1520, to_w=10)
line_successive.scale_to(from_x=1600, to_x=1620, to_w=40)
line_successive.shift_to(from_x=1700, to_x=1720, to_y=50)
line_successive.shift_to(from_x=1800, to_x=1820, to_y=100)
line_successive.scale_to(from_x=1850, to_x=1900, to_w=5)
line_successive.scale_to(from_x=1920, to_x=1970, to_w=100)





# -----------------------------------------------------------------------------
# 2. Overlapping Transformations
# -----------------------------------------------------------------------------

line_overlapping = Lineage(
    diagram = diagram,
    color   = color_red,
    start_x = 0,
    start_y = 200,
    start_w = 5
)
line_overlapping.scale_to(from_x=100,  to_x=299,  to_w=30)
line_overlapping.shift_to(from_x=100,  to_x=299,  to_y=150)
line_overlapping.scale_to(from_x=400,  to_x=599,  to_w=5)
line_overlapping.shift_to(from_x=400,  to_x=599,  to_y=200)
line_overlapping.scale_to(from_x=600,  to_x=999,  to_w=40)
line_overlapping.shift_to(from_x=630,  to_x=660,  to_y=150)
line_overlapping.shift_to(from_x=670,  to_x=699,  to_y=200)
line_overlapping.shift_to(from_x=710,  to_x=799,  to_y=150)
line_overlapping.shift_to(from_x=810,  to_x=899,  to_y=200)
line_overlapping.shift_to(from_x=930,  to_x=999,  to_y=150)
line_overlapping.shift_to(from_x=1100, to_x=1950, to_y=200)
line_overlapping.scale_to(from_x=1150, to_x=1299, to_w=5)
line_overlapping.scale_to(from_x=1350, to_x=1499, to_w=40)
line_overlapping.scale_to(from_x=1550, to_x=1599, to_w=5)
line_overlapping.scale_to(from_x=1650, to_x=1699, to_w=40)
line_overlapping.scale_to(from_x=1740, to_x=1760, to_w=5)
line_overlapping.scale_to(from_x=1780, to_x=1799, to_w=40)
line_overlapping.scale_to(from_x=1820, to_x=1830, to_w=5)
line_overlapping.scale_to(from_x=1840, to_x=1850, to_w=40)
line_overlapping.scale_to(from_x=1860, to_x=1870, to_w=5)
line_overlapping.scale_to(from_x=1880, to_x=1890, to_w=40)
line_overlapping.scale_to(from_x=1900, to_x=1910, to_w=5)
line_overlapping.scale_to(from_x=1920, to_x=1930, to_w=40)
line_overlapping.scale_to(from_x=1940, to_x=1950, to_w=5)
line_overlapping.scale_to(from_x=1960, to_x=1970, to_w=40)





# -----------------------------------------------------------------------------
# 3. Trunk and Branches
# -----------------------------------------------------------------------------

line_trunk = Lineage(
    diagram = diagram,
    color   = color_green,
    start_x = 0,
    start_y = 250,
    start_w = 40,
    z       = 1,
)
line_trunk.shift_to(from_x= 600, to_x= 700, to_y=300)
line_trunk.shift_to(from_x=1200, to_x=1500, to_y=250)
line_trunk.scale_to(from_x=1200, to_x=1500, to_w=10)
line_trunk.shift_to(from_x=1600, to_x=1900, to_y=300)
line_trunk.scale_to(from_x=1600, to_x=1900, to_w=40)
line_trunk.terminate_at(2000)

# Branch 1
line_branch_1 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 100,
    transition_to_x = 200,
    new_color       = color_dark_green,
    new_target_w    = 10,
    new_target_y    = 300,
)
line_branch_1.end_at_lineage(target_lineage=line_trunk, transition_from_x=300, end_x=400)

# Branch 2
line_branch_2 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 500,
    transition_to_x = 550,
    new_color       = color_dark_green,
    new_target_w    = 10,
    new_target_y    = 300,
)
line_branch_2.shift_to(from_x=600, to_x=700, to_y=250)
line_branch_2.end_at_lineage(target_lineage=line_trunk, transition_from_x=750, end_x=800)

# Branch 3
line_branch_3 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 900,
    transition_to_x = 1000,
    new_color       = color_dark_green,
    new_target_w    = 10,
    new_target_y    = 250,
)
line_branch_3.end_at_lineage(target_lineage=line_trunk, transition_from_x=1100, end_x=1200)

# Branch 4
line_branch_4 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 1300,
    transition_to_x = 1500,
    new_color       = color_dark_green,
    new_target_w    = 5,
    new_target_y    = 320,
)
line_branch_4.end_at_lineage(target_lineage=line_trunk, transition_from_x=1600, end_x=1800)

# Branch 5
line_branch_5 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 1350,
    transition_to_x = 1500,
    new_color       = color_dark_green,
    new_target_w    = 5,
    new_target_y    = 300,
)
line_branch_5.end_at_lineage(target_lineage=line_trunk, transition_from_x=1600, end_x=1750)

# Branch 6
line_branch_6 = Lineage.create_from_lineage(
    parent          = line_trunk,
    start_x         = 1400,
    transition_to_x = 1500,
    new_color       = color_dark_green,
    new_target_w    = 5,
    new_target_y    = 280,
)
line_branch_6.end_at_lineage(target_lineage=line_trunk, transition_from_x=1600, end_x=1700)





# -----------------------------------------------------------------------------
# 4. Generations (Split & Merge)
# -----------------------------------------------------------------------------

line_gen1 = Lineage(
    diagram = diagram,
    color   = color_yellow,
    start_x = 0,
    start_y = 375,
    start_w = 40
)

# Split 1 -> 3
line_gen2_1, line_gen2_2, line_gen2_3 = line_gen1.split(
    start_x    = 100,
    split_to_x = 200,
    children_specs = [
        {'color': color_dark_yellow, 'target_w': 20, 'target_y': 350},
        {'color': color_dark_yellow, 'target_w': 10, 'target_y': 375},
        {'color': color_dark_yellow, 'target_w': 5,  'target_y': 400},
    ]
)

line_gen2_1.scale_to(from_x=300, to_x=400, to_w=5)
line_gen2_2.scale_to(from_x=300, to_x=400, to_w=10)
line_gen2_3.scale_to(from_x=300, to_x=400, to_w=20)

# Merge 3 -> 1
line_gen3 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_yellow,
    merge_from_x = 500,
    start_x      = 600,
    start_y      = 375,
    start_w      = 40,
    parents      = [line_gen2_1, line_gen2_2, line_gen2_3]
)
line_gen3.scale_to(from_x=700, to_x=800, to_w=5)
line_gen3.shift_to(from_x=700, to_x=800, to_y=350)

# Split 1 -> 2
line_gen4_1, line_gen4_2 = line_gen3.split(
    start_x    = 900,
    split_to_x = 1000,
    children_specs = [
        {'color': color_dark_yellow, 'target_w': 10, 'target_y': 375},
        {'color': color_dark_yellow, 'target_w': 10, 'target_y': 400},
    ]
)

# Split 2 -> 4 (2 each)
line_gen5_1, line_gen5_2 = line_gen4_1.split(
    start_x    = 1100,
    split_to_x = 1200,
    children_specs = [
        {'color': color_yellow, 'target_w': 5, 'target_y': 350},
        {'color': color_yellow, 'target_w': 5, 'target_y': 370},
    ]
)
line_gen5_3, line_gen5_4 = line_gen4_2.split(
    start_x    = 1100,
    split_to_x = 1200,
    children_specs = [
        {'color': color_yellow, 'target_w': 5, 'target_y': 380},
        {'color': color_yellow, 'target_w': 5, 'target_y': 400},
    ]
)

# Merge 4 -> 2
line_gen6_1 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_dark_yellow,
    merge_from_x = 1300,
    start_x      = 1400,
    start_y      = 350,
    start_w      = 20,
    parents      = [line_gen5_1, line_gen5_3]
)
line_gen6_2 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_dark_yellow,
    merge_from_x = 1300,
    start_x      = 1400,
    start_y      = 400,
    start_w      = 20,
    parents      = [line_gen5_2, line_gen5_4]
)

# Merge 2 -> 1
line_gen7 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_yellow,
    merge_from_x = 1500,
    start_x      = 1600,
    start_y      = 350,
    start_w      = 5,
    parents      = [line_gen6_1, line_gen6_2]
)
line_gen7.scale_to(from_x=1700, to_x=1800, to_w=40)
line_gen7.shift_to(from_x=1700, to_x=1800, to_y=400)





# -----------------------------------------------------------------------------
# 5. Simple Bundle
# -----------------------------------------------------------------------------

simple_bundle = Bundle(diagram, start_x=0, start_y=500, margin=3)

simple_bundle_line_1 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_blue,
    start_x   = 0,
    start_w   = 10,
    in_bundle = simple_bundle,
)
simple_bundle_line_2 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_red,
    start_x   = 0,
    start_w   = 10,
    in_bundle = simple_bundle,
)
simple_bundle_line_3 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_green,
    start_x   = 0,
    start_w   = 10,
    in_bundle = simple_bundle,
)

simple_bundle_line_1.scale_to(from_x=100, to_x=150, to_w=30)
simple_bundle_line_2.scale_to(from_x=100, to_x=150, to_w=5)
simple_bundle_line_3.scale_to(from_x=100, to_x=150, to_w=5)

simple_bundle_line_1.scale_to(from_x=200, to_x=250, to_w=5)
simple_bundle_line_2.scale_to(from_x=200, to_x=250, to_w=30)
simple_bundle_line_3.scale_to(from_x=200, to_x=250, to_w=5)

simple_bundle_line_1.scale_to(from_x=300, to_x=350, to_w=5)
simple_bundle_line_2.scale_to(from_x=300, to_x=350, to_w=5)
simple_bundle_line_3.scale_to(from_x=300, to_x=350, to_w=30)

simple_bundle_line_1.scale_to(from_x=400, to_x=450, to_w=5)
simple_bundle_line_2.scale_to(from_x=400, to_x=450, to_w=5)
simple_bundle_line_3.scale_to(from_x=400, to_x=450, to_w=5)

simple_bundle.shift_to(from_x=500, to_x=550, to_y=475)

simple_bundle_line_1.scale_to(from_x=600, to_x=650, to_w=30)
simple_bundle_line_2.scale_to(from_x=600, to_x=650, to_w=30)
simple_bundle_line_3.scale_to(from_x=600, to_x=650, to_w=30)

simple_bundle_line_1.scale_to(from_x=700, to_x=750, to_w=5)
simple_bundle_line_2.scale_to(from_x=700, to_x=750, to_w=5)
simple_bundle_line_3.scale_to(from_x=700, to_x=750, to_w=5)

simple_bundle.shift_to(from_x=800, to_x=850, to_y=500)

simple_bundle.shift_to(from_x=900, to_x=999, to_y=450)
simple_bundle_line_1.scale_to(from_x=900, to_x=999, to_w=15)
simple_bundle_line_2.scale_to(from_x=900, to_x=999, to_w=15)
simple_bundle_line_3.scale_to(from_x=900, to_x=999, to_w=15)

simple_bundle.shift_to(from_x=1000, to_x=1099, to_y=500)
simple_bundle_line_1.scale_to(from_x=1000, to_x=1099, to_w=5)
simple_bundle_line_2.scale_to(from_x=1000, to_x=1099, to_w=5)
simple_bundle_line_3.scale_to(from_x=1000, to_x=1099, to_w=5)

simple_bundle.shift_to(from_x=1200, to_x=1550, to_y=450)
simple_bundle_line_1.scale_to(from_x=1200, to_x=1250, to_w=30)
simple_bundle_line_1.scale_to(from_x=1300, to_x=1350, to_w=5)
simple_bundle_line_2.scale_to(from_x=1300, to_x=1350, to_w=30)
simple_bundle_line_2.scale_to(from_x=1400, to_x=1450, to_w=5)
simple_bundle_line_3.scale_to(from_x=1400, to_x=1450, to_w=30)
simple_bundle_line_3.scale_to(from_x=1500, to_x=1550, to_w=5)

simple_bundle.shift_to(from_x=1600, to_x=1950, to_y=500)
simple_bundle_line_1.scale_to(from_x=1625, to_x=1675, to_w=40)
simple_bundle_line_1.scale_to(from_x=1675, to_x=1725, to_w=5)
simple_bundle_line_2.scale_to(from_x=1725, to_x=1775, to_w=40)
simple_bundle_line_2.scale_to(from_x=1775, to_x=1825, to_w=5)
simple_bundle_line_3.scale_to(from_x=1825, to_x=1875, to_w=40)
simple_bundle_line_3.scale_to(from_x=1875, to_x=1925, to_w=5)

simple_bundle_line_1.terminate_at(2000)
simple_bundle_line_2.terminate_at(2000)





# -----------------------------------------------------------------------------
# 6. Host Bundle (Join & Leave)
# -----------------------------------------------------------------------------

host_bundle = Bundle(diagram, start_x=0, start_y=600, margin=3)

host_bundle_line_1 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_blue,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_2 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_red,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_3 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_green,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_4 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_yellow,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)

host_bundle_line_4.leave(from_x=100, to_x=150, from_assembly=host_bundle, to_y=550)
host_bundle_line_4.join (from_x=200, to_x=250,   to_assembly=host_bundle, index=0)
host_bundle_line_4.leave(from_x=300, to_x=350, from_assembly=host_bundle, to_y=550)
host_bundle_line_4.join (from_x=400, to_x=450,   to_assembly=host_bundle, index=1)
host_bundle_line_4.leave(from_x=500, to_x=550, from_assembly=host_bundle, to_y=550)
host_bundle_line_4.join (from_x=600, to_x=650,   to_assembly=host_bundle, index=2)
host_bundle_line_4.leave(from_x=700, to_x=750, from_assembly=host_bundle, to_y=550)
host_bundle_line_4.join (from_x=800, to_x=850,   to_assembly=host_bundle, index=3)

host_bundle_line_1.leave(from_x=900,  to_x=950,  from_assembly=host_bundle, to_y=550)
host_bundle_line_1.join (from_x=1000, to_x=1050,   to_assembly=host_bundle, index=3)
host_bundle_line_2.leave(from_x=1100, to_x=1150, from_assembly=host_bundle, to_y=550)
host_bundle_line_2.join (from_x=1200, to_x=1250,   to_assembly=host_bundle, index=3)
host_bundle_line_3.leave(from_x=1300, to_x=1350, from_assembly=host_bundle, to_y=550)
host_bundle_line_3.join (from_x=1400, to_x=1450,   to_assembly=host_bundle, index=3)

host_bundle_line_1.leave(from_x=1500, to_x=1550, from_assembly=host_bundle, to_y=550)
host_bundle_line_2.leave(from_x=1600, to_x=1650, from_assembly=host_bundle, to_y=565)
host_bundle_line_3.leave(from_x=1700, to_x=1750, from_assembly=host_bundle, to_y=550)

host_bundle_line_1.join(from_x=1700, to_x=1750, to_assembly=host_bundle, index=0)
host_bundle_line_2.join(from_x=1800, to_x=1850, to_assembly=host_bundle, index=0)
host_bundle_line_3.join(from_x=1900, to_x=1950, to_assembly=host_bundle, index=0)

host_bundle_line_1.terminate_at(2000)
host_bundle_line_2.terminate_at(2000)
host_bundle_line_3.terminate_at(2000)





# -----------------------------------------------------------------------------
# 7. Split & Merge Cycles
# -----------------------------------------------------------------------------

source_line = Lineage(diagram, color_white, 0, 675, 40)

# Cycle 1
split_lines = source_line.split(
    start_x    = 100,
    split_to_x = 200,
    children_specs = [
        {'color': color_blue,   'target_w': 5, 'target_y': 650},
        {'color': color_red,    'target_w': 5, 'target_y': 666.6},
        {'color': color_green,  'target_w': 5, 'target_y': 683.4},
        {'color': color_yellow, 'target_w': 5, 'target_y': 700},
    ]
)
merged_line = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 300,
    start_x      = 400,
    start_y      = 675,
    start_w      = 40,
    parents      = split_lines,
)
merged_line.scale_to(from_x=500, to_x=550, to_w=5)

# Cycle 2
split_lines = merged_line.split(
    start_x    = 600,
    split_to_x = 700,
    children_specs = [
        {'color': color_blue,   'target_w': 12, 'target_y': 650},
        {'color': color_red,    'target_w': 12, 'target_y': 666.6},
        {'color': color_green,  'target_w': 12, 'target_y': 683.4},
        {'color': color_yellow, 'target_w': 12, 'target_y': 700},
    ]
)
merged_line = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 800,
    start_x      = 900,
    start_y      = 675,
    start_w      = 5,
    parents      = split_lines,
)
merged_line.scale_to(from_x=1000, to_x=1050, to_w=40)

# Cycle 3
split_lines = merged_line.split(
    start_x    = 1100,
    split_to_x = 1200,
    children_specs = [
        {'color': color_blue,   'target_w': 20, 'target_y': 650},
        {'color': color_red,    'target_w': 15, 'target_y': 675},
        {'color': color_green,  'target_w': 10, 'target_y': 690},
        {'color': color_yellow, 'target_w': 5,  'target_y': 700},
    ]
)
merged_line = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1300,
    start_x      = 1400,
    start_y      = 675,
    start_w      = 40,
    parents      = split_lines,
)
merged_line.scale_to(from_x=1500, to_x=1550, to_w=5)

# Cycle 4
split_lines = merged_line.split(
    start_x    = 1600,
    split_to_x = 1700,
    children_specs = [
        {'color': color_blue,   'target_w': 5,  'target_y': 650},
        {'color': color_red,    'target_w': 10, 'target_y': 660},
        {'color': color_green,  'target_w': 15, 'target_y': 675},
        {'color': color_yellow, 'target_w': 20, 'target_y': 700},
    ]
)
merged_line = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1800,
    start_x      = 1900,
    start_y      = 675,
    start_w      = 5,
    parents      = split_lines,
)





# -----------------------------------------------------------------------------
# 8. Continuing Splits
# -----------------------------------------------------------------------------

source_line = Lineage(
    diagram = diagram,
    color   = color_white,
    start_x = 0,
    start_y = 800,
    start_w = 40,
    z       = 1,
)

# Split 1
split_line_1 = Lineage.create_split_from(
    parent          = source_line,
    start_x         = 100,
    split_to_x      = 200,
    new_color       = color_blue,
    new_target_w    = 10,
    new_target_y    = 750,
    parent_target_w = 30,
    parent_target_y = 800,
)

# Split 2
split_line_2 = Lineage.create_split_from(
    parent          = source_line,
    start_x         = 300,
    split_to_x      = 400,
    new_color       = color_red,
    new_target_w    = 10,
    new_target_y    = 762,
    parent_target_w = 20,
    parent_target_y = 800,
)

# Split 3
split_line_3 = Lineage.create_split_from(
    parent          = source_line,
    start_x         = 500,
    split_to_x      = 600,
    new_color       = color_green,
    new_target_w    = 10,
    new_target_y    = 774,
    parent_target_w = 10,
    parent_target_y = 800,
)

# Split 4
split_line_4 = Lineage.create_split_from(
    parent          = source_line,
    start_x         = 700,
    split_to_x      = 800,
    new_color       = color_yellow,
    new_target_w    = 10,
    new_target_y    = 786,
    parent_target_w = 10,
    parent_target_y = 800,
)

split_line_4.merge_into(
    target_lineage = source_line,
    merge_from_x   = 900,
    end_x          = 1000,
    target_w       = 10,
)

split_line_3.merge_into(
    target_lineage = source_line,
    merge_from_x   = 1100,
    end_x          = 1200,
    target_w       = 20,
)

split_line_2.merge_into(
    target_lineage = source_line,
    merge_from_x   = 1300,
    end_x          = 1400,
    target_w       = 30,
)

split_line_1.merge_into(
    target_lineage = source_line,
    merge_from_x   = 1500,
    end_x          = 1600,
    target_w       = 40,
)

source_line.terminate_at(2000)





# -----------------------------------------------------------------------------
# 9. Merge and split inside bundle
# -----------------------------------------------------------------------------

host_bundle = Bundle(diagram, start_x=0, start_y=875, margin=3)

host_bundle_line_1 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_blue,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_2 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_red,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_3 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_green,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_4 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_yellow,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)

host_bundle_merged_line_1 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 100,
    start_x      = 150,
    start_w      = 20,
    parents      = [host_bundle_line_1, host_bundle_line_2,],
    in_bundle    = host_bundle,
    index        = 0,
)
host_bundle_line_2, host_bundle_line_1 = host_bundle_merged_line_1.split(
    start_x    = 200,
    split_to_x = 250,
    children_specs = [
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

host_bundle_merged_line_2 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 300,
    start_x      = 350,
    start_w      = 20,
    parents      = [host_bundle_line_2, host_bundle_line_3],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_3, host_bundle_line_2 = host_bundle_merged_line_2.split(
    start_x    = 400,
    split_to_x = 450,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)

host_bundle_merged_line_3 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 500,
    start_x      = 550,
    start_w      = 20,
    parents      = [host_bundle_line_3, host_bundle_line_4,],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_4, host_bundle_line_3 = host_bundle_merged_line_3.split(
    start_x    = 600,
    split_to_x = 650,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
    ]
)

host_bundle_merged_line_1 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 700,
    start_x      = 750,
    start_w      = 5,
    parents      = [host_bundle_line_1, host_bundle_line_2,],
    in_bundle    = host_bundle,
    index        = 0,
)
host_bundle_line_2, host_bundle_line_1 = host_bundle_merged_line_1.split(
    start_x    = 800,
    split_to_x = 850,
    children_specs = [
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

host_bundle_merged_line_2 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 900,
    start_x      = 950,
    start_w      = 5,
    parents      = [host_bundle_line_2, host_bundle_line_3],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_3, host_bundle_line_2 = host_bundle_merged_line_2.split(
    start_x    = 1000,
    split_to_x = 1050,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)

host_bundle_merged_line_3 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1100,
    start_x      = 1150,
    start_w      = 5,
    parents      = [host_bundle_line_3, host_bundle_line_4,],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_4, host_bundle_line_3 = host_bundle_merged_line_3.split(
    start_x    = 1200,
    split_to_x = 1250,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
    ]
)

host_bundle_merged_line_1 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1300,
    start_x      = 1350,
    start_w      = 40,
    parents      = [host_bundle_line_1, host_bundle_line_2,],
    in_bundle    = host_bundle,
    index        = 0,
)
host_bundle_line_2, host_bundle_line_1 = host_bundle_merged_line_1.split(
    start_x    = 1400,
    split_to_x = 1450,
    children_specs = [
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

host_bundle_merged_line_2 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1500,
    start_x      = 1550,
    start_w      = 40,
    parents      = [host_bundle_line_2, host_bundle_line_3],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_3, host_bundle_line_2 = host_bundle_merged_line_2.split(
    start_x    = 1600,
    split_to_x = 1650,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)

host_bundle_merged_line_3 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1700,
    start_x      = 1750,
    start_w      = 40,
    parents      = [host_bundle_line_3, host_bundle_line_4,],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_4, host_bundle_line_3 = host_bundle_merged_line_3.split(
    start_x    = 1800,
    split_to_x = 1850,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
    ]
)





# -----------------------------------------------------------------------------
# 9. Merge and split to/from bundle
# -----------------------------------------------------------------------------

host_bundle = Bundle(diagram, start_x=0, start_y=1000, margin=3)

host_bundle_line_1 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_blue,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_2 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_red,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_3 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_green,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)
host_bundle_line_4 = Lineage.create_in_bundle(
    diagram   = diagram,
    color     = color_yellow,
    start_x   = 0,
    start_w   = 10,
    in_bundle = host_bundle,
)

merged_line_1 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 100,
    start_x      = 150,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_1, host_bundle_line_2,],
)
host_bundle_line_2, host_bundle_line_1 = merged_line_1.split(
    start_x    = 200,
    split_to_x = 250,
    children_specs = [
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

merged_line_2 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 300,
    start_x      = 350,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_2, host_bundle_line_3],
)
host_bundle_line_3, host_bundle_line_2 = merged_line_2.split(
    start_x    = 400,
    split_to_x = 450,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)

merged_line_3 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 500,
    start_x      = 550,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_3, host_bundle_line_4,],
)
host_bundle_line_4, host_bundle_line_3 = merged_line_3.split(
    start_x    = 600,
    split_to_x = 650,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
        {
            "color":     color_green,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     2,
        },
    ]
)

merged_line_4 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 700,
    start_x      = 750,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_1, host_bundle_line_4],
)
host_bundle_line_4, host_bundle_line_1 = merged_line_4.split(
    start_x    = 800,
    split_to_x = 850,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     3,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

merged_line_5 = Lineage.create_in_bundle_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 900,
    start_x      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_1, host_bundle_line_4],
    in_bundle    = host_bundle,
    index        = 2,
)
host_bundle_line_4, host_bundle_line_1 = merged_line_5.split(
    start_x    = 1000,
    split_to_x = 1050,
    children_specs = [
        {
            "color":     color_yellow,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     4,
        },
        {
            "color":     color_blue,
            "target_w":  10,
            "in_bundle": host_bundle,
            "index":     0,
        },
    ]
)

merged_line_6 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1100,
    start_x      = 1150,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_2, host_bundle_line_3],
)
host_bundle_line_3, host_bundle_line_2 = merged_line_6.split(
    start_x    = 1200,
    split_to_x = 1250,
    children_specs = [
        {
            "color":    color_green,
            "target_w": 10,
            "target_y": 940,
        },
        {
            "color":    color_red,
            "target_w": 10,
            "target_y": 960,
        },
    ]
)
host_bundle_line_3.join(from_x=1300, to_x=1350, to_assembly=host_bundle, index=1)
host_bundle_line_2.join(from_x=1300, to_x=1350, to_assembly=host_bundle, index=1)

merged_line_7 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1400,
    start_x      = 1450,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_2, host_bundle_line_3],
)
host_bundle_line_3, host_bundle_line_2 = merged_line_7.split(
    start_x    = 1500,
    split_to_x = 1550,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "target_y":  940,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "target_y":  960,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)
merged_line_8 = Lineage.create_from_merge(
    diagram      = diagram,
    color        = color_white,
    merge_from_x = 1600,
    start_x      = 1650,
    start_y      = 950,
    start_w      = 20,
    parents      = [host_bundle_line_2, host_bundle_line_3],
)
host_bundle_line_3, host_bundle_line_2 = merged_line_8.split(
    start_x    = 1700,
    split_to_x = 1750,
    children_specs = [
        {
            "color":     color_green,
            "target_w":  10,
            "target_y":  940,
        },
        {
            "color":     color_red,
            "target_w":  10,
            "target_y":  960,
            "in_bundle": host_bundle,
            "index":     1,
        },
    ]
)
host_bundle_line_3.join(from_x=1800, to_x=1850, to_assembly=host_bundle, index=2)





# -----------------------------------------------------------------------------
# 10. Orbit
# -----------------------------------------------------------------------------

main_line = Lineage(
    diagram = diagram,
    color   = color_white,
    start_x = 0,
    start_y = 1100,
    start_w = 20
)

satellite_line_1 = Lineage(
    diagram = diagram,
    color   = color_blue,
    start_x = 0,
    start_y = 1050,
    start_w = 5
)
satellite_line_2 = Lineage(
    diagram = diagram,
    color   = color_red,
    start_x = 0,
    start_y = 1060,
    start_w = 5
)
satellite_line_3 = Lineage(
    diagram = diagram,
    color   = color_green,
    start_x = 0,
    start_y = 1140,
    start_w = 5
)
satellite_line_4 = Lineage(
    diagram = diagram,
    color   = color_yellow,
    start_x = 0,
    start_y = 1150,
    start_w = 5
)

orbit = Orbit(diagram, main_line, margin=3)

satellite_line_1.join(from_x=150, to_x=200, to_assembly=orbit, index=+2)
satellite_line_2.join(from_x=100, to_x=150, to_assembly=orbit, index=+1)
satellite_line_3.join(from_x=100, to_x=150, to_assembly=orbit, index=-1)
satellite_line_4.join(from_x=150, to_x=200, to_assembly=orbit, index=-2)

main_line.scale_to(from_x=250, to_x=300, to_w=5)
main_line.scale_to(from_x=350, to_x=400, to_w=40)
main_line.scale_to(from_x=450, to_x=500, to_w=20)

satellite_line_2.scale_to(from_x=550, to_x=600, to_w=20)
satellite_line_1.scale_to(from_x=600, to_x=650, to_w=20)
satellite_line_1.scale_to(from_x=700, to_x=750, to_w=5)
satellite_line_2.scale_to(from_x=700, to_x=750, to_w=5)

satellite_line_3.scale_to(from_x=750, to_x=800, to_w=20)
satellite_line_4.scale_to(from_x=800, to_x=850, to_w=20)
satellite_line_4.scale_to(from_x=900, to_x=950, to_w=5)
satellite_line_3.scale_to(from_x=900, to_x=950, to_w=5)

main_line.shift_to(from_x=1000, to_x=1050, to_y=1070)
main_line.shift_to(from_x=1100, to_x=1200, to_y=1130)
main_line.shift_to(from_x=1250, to_x=1300, to_y=1100)

satellite_line_2.leave(from_x=1350, to_x=1400, from_assembly=orbit, to_y=1050)
satellite_line_3.leave(from_x=1350, to_x=1400, from_assembly=orbit, to_y=1150)

satellite_line_1.leave(from_x=1400, to_x=1450, from_assembly=orbit, to_y=1060)
satellite_line_4.leave(from_x=1400, to_x=1450, from_assembly=orbit, to_y=1140)

satellite_line_1.join(from_x=1500, to_x=1550, to_assembly=orbit, index=-1)
satellite_line_4.join(from_x=1500, to_x=1550, to_assembly=orbit, index=+1)

satellite_line_2.join(from_x=1550, to_x=1600, to_assembly=orbit, index=-1)
satellite_line_3.join(from_x=1550, to_x=1600, to_assembly=orbit, index=+1)





# -----------------------------------------------------------------------------
# Generate
# -----------------------------------------------------------------------------
diagram.generate("comprehensive_example.svg")
