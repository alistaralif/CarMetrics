export const ROUTE_ORDER: string[] = [
    "/",
    "/quick-start",
    "/analysis",
  ];
  
  export function getRouteIndex(pathname: string) {
    const idx = ROUTE_ORDER.indexOf(pathname);
    return idx === -1 ? 0 : idx;
  }  