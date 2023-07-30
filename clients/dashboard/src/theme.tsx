import { StyleFunctionProps, extendTheme, keyframes } from "@chakra-ui/react";
import { mode } from "@chakra-ui/theme-tools";


export const theme = extendTheme({
  styles: {
    global: {
      body: {
        bg: "#111",
        color: "white",
      },
      h1: {
        color: "blue.500",
        marginBottom: "0.2em",
      },
      h2: {
        fontSize: "1.5em",
        color: "blue.300",
        marginBottom: "0.5em",
      },
      modal: {
        bg: "blue.900",
      },
    },
  },
});
