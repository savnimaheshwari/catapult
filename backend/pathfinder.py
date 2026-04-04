import networkx as nx
import math

def calculate_safe_route(start_lat: float, start_lng: float, dest_lat: float, dest_lng: float, damage_points: list):
    """
    Uses NetworkX to find the shortest path avoiding damage points.
    We'll represent the area as a grid graph.
    """
    
    # 1. Create a logical grid (e.g. 30x30 nodes between start and dest)
    grid_size = 30
    G = nx.grid_2d_graph(grid_size, grid_size)
    
    # Add diagonal edges for smoother paths
    G.add_edges_from((
        ((x, y), (x+1, y+1))
        for x in range(grid_size-1)
        for y in range(grid_size-1)
    ))
    G.add_edges_from((
        ((x+1, y), (x, y+1))
        for x in range(grid_size-1)
        for y in range(grid_size-1)
    ))

    min_lat = min(start_lat, dest_lat) - 0.005
    max_lat = max(start_lat, dest_lat) + 0.005
    min_lng = min(start_lng, dest_lng) - 0.005
    max_lng = max(start_lng, dest_lng) + 0.005
    
    lat_step = (max_lat - min_lat) / grid_size
    lng_step = (max_lng - min_lng) / grid_size
    
    # helper: coordinate to grid index
    def coord_to_grid(lat, lng):
        x = int(min(grid_size-1, max(0, (lng - min_lng) / lng_step)))
        y = int(min(grid_size-1, max(0, (lat - min_lat) / lat_step)))
        return (x, y)
        
    start_node = coord_to_grid(start_lat, start_lng)
    dest_node = coord_to_grid(dest_lat, dest_lng)
    
    # Ensure start and dest are within grid
    G.add_node(start_node)
    G.add_node(dest_node)

    # Convert damage points to grid zones and remove them
    blocked_nodes = set()
    for point in damage_points:
        node = coord_to_grid(point['lat'], point['lng'])
        if node not in (start_node, dest_node):
            blocked_nodes.add(node)
                        
    G.remove_nodes_from(blocked_nodes)
    
    # 2. Pathfinding
    try:
        path = nx.shortest_path(G, source=start_node, target=dest_node)
        
        # 3. Convert back to coordinates
        route_coords = []
        for x, y in path:
            lng = min_lng + x * lng_step
            lat = min_lat + y * lat_step
            route_coords.append([lng, lat]) # GeoJSON format: [lng, lat]
            
        # Guarantee endpoint accuracy
        if route_coords:
            route_coords[0] = [start_lng, start_lat]
            route_coords[-1] = [dest_lng, dest_lat]
            
        return route_coords
    except nx.NetworkXNoPath:
        return None # No possible route
