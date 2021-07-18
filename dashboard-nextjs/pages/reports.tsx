import { Box } from "@chakra-ui/layout";
import axios, { AxiosError } from "axios";
import { useEffect } from "react";

function Reports() {
  useEffect(() => {
    axios.get("/api/sku").then(
      (res) => {
        console.log("Reports > res", res);
      },
      (err: AxiosError) => {
        console.log("Reports > error", err.message);
      }
    );
  }, []);
  return <Box>Product List</Box>;
}

export default Reports;
