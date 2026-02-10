"use client";

import { AgGridReact } from "ag-grid-react";
import type { ColDef, ColGroupDef, ICellRendererParams } from "ag-grid-community";
import type { CarListing } from "@/lib/types";
import { themeQuartz, colorSchemeLightWarm, colorSchemeDark } from "ag-grid-community";
import { useState, useEffect } from "react";

type ResultsTableProps = {
  data: CarListing[];
  wrapperClassName?: string;
  enableCellTextSelection?: boolean;
  suppressCellFocus?: boolean;
};

const darkTheme = themeQuartz.withPart(colorSchemeDark);
const lightTheme = themeQuartz.withPart(colorSchemeLightWarm);

function useColorScheme() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check initial preference
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    setIsDark(mediaQuery.matches);

    // Listen for changes
    const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
    mediaQuery.addEventListener("change", handler);

    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  return isDark;
}

export default function ResultsTable({
  data,
  wrapperClassName = "results-table-wrapper",
}: ResultsTableProps) {
  const isDarkMode = useColorScheme();
  const theme = isDarkMode ? darkTheme : lightTheme;
  const colDefs: (ColDef<CarListing> | ColGroupDef<CarListing>)[] = [
    { field: "model", headerName: "Model", pinned: 'left', width: 370, wrapText: true, autoHeight: true },
    {
        headerName: "Car Details",
        children: [
            { field: "price", headerName: "Price" },
            { field: "depreciation", headerName: "Depreciation" },
            { field: "end_coe_rebates", headerName: "PARF Rebate", columnGroupShow: 'open' },
            { field: "road_tax", headerName: "Road Tax", columnGroupShow: 'open' },
            { field: "reg_date", headerName: "Reg Date", columnGroupShow: 'open' },
            { field: "coe_left", headerName: "COE Left", columnGroupShow: 'open' },
        ]
    },
    { 
        headerName: "Financing Estimates", 
        children: [
            { field: "loan_term_months", headerName: "Loan Term (Months)" },
            { field: "zero_dp_monthly", headerName: "$0 DP Monthly", columnGroupShow: 'open' },
            { field: "tenk_dp_monthly", headerName: "$10K DP Monthly" },
            { field: "twentyk_dp_monthly", headerName: "$20K DP Monthly", columnGroupShow: 'open' },
            { field: "thirtyk_dp_monthly", headerName: "$30K DP Monthly", columnGroupShow: 'open' },
            { field: "fortyk_dp_monthly", headerName: "$40K DP Monthly", columnGroupShow: 'open' },
            { field: "fiftyk_dp_monthly", headerName: "$50K DP Monthly", columnGroupShow: 'open' },
        ] 
    },
    {
        headerName: "Performance",
        children: [
            { field: "power_bhp", headerName: "Power (BHP)", columnGroupShow: 'open' },
            { field: "curb_weight_kg", headerName: "Curb Weight (kg)", columnGroupShow: 'open' },
            { field: "power_to_weight", headerName: "Power-to-Weight" },
            { field: "engine_cc", headerName: "Engine (cc)", columnGroupShow: 'open' },
            { field: "power_kw", headerName: "Power (kW)", columnGroupShow: 'open'},
            { field: "transmission", headerName: "Transmission", columnGroupShow: 'open' },
        ]
    },
    {
        headerName: "Additional Info",
        children: [
            { field: "vehicle_type", headerName: "Vehicle Type", columnGroupShow: 'open' },
            { field: "type", headerName: "Category", columnGroupShow: 'open' },
            { field: "mileage", headerName: "Mileage (km)" },
            { field: "no_owners", headerName: "No. of Owners" },
            { field: "coe", headerName: "COE", columnGroupShow: 'open' },
            { field: "arf", headerName: "ARF", columnGroupShow: 'open' },
            { field: "omv", headerName: "OMV", columnGroupShow: 'open' },
            { field: "url", headerName: "Sgcarmart URL", columnGroupShow: 'open', 
              cellRenderer: (params: ICellRendererParams<CarListing, string>) => {
                const url = params.value as string | undefined;
                if (!url) return null;
          
                return (
                  <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "rgb(50, 97, 215)", textDecoration: "underline" }}
                  >
                    View listing
                  </a>
                );
            },  
          },
        ]
    },
    
    
    // { field: "photos", headerName: "Photos"},
  ];

  return (
    <div className={`${wrapperClassName}-table-wrapper`}>
      <AgGridReact<CarListing>
        rowData={data}
        columnDefs={colDefs}
        theme={theme}
        enableCellTextSelection={true}
        suppressCellFocus={true}
      />
    </div>
  );
}
