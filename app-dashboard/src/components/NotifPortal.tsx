import ReactDOM from "react-dom";
import { useEffect, useState } from "react";

type Props = {
  el: string;
  children: React.ReactNode;
};

function NotifPortal({ children, el }: Props) {
  const [domReady, setDomReady] = useState(false);

  useEffect(() => {
    setTimeout(() => {
      setDomReady(true);
    }, 100);
  }, []);

  return document.getElementById(el) != undefined
    ? ReactDOM.createPortal(
        children,
        document.getElementById(el) as HTMLElement
      )
    : null;
}

export default NotifPortal;
