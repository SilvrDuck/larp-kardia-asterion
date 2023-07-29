import { StyleFunctionProps, extendTheme } from "@chakra-ui/react";
import { mode } from "@chakra-ui/theme-tools";
import bg from "@assets/bg.png";

export const theme = extendTheme({
  styles: {
    global: (props: StyleFunctionProps) => ({
      body: {
        color: 'default',
        bg: '#111',
        backgroundImage: bg,
    },
    }),
  },
})