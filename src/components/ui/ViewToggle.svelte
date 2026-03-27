<script lang="ts">



  export type ViewMode = "grid" | "list";



  export let value: ViewMode = "grid";



  export let onChange: (mode: ViewMode) => void = () => {};



  export let wrapperClass = "flex gap-1";



  export let size: "sm" | "md" = "md";



  const iconSizeClass = size === "sm" ? "h-4 w-4" : "h-5 w-5";



  const baseButtonClass =



    "p-1 border rounded transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-gray-900";



  const activeClass =



    "bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-200 border-blue-300 dark:border-blue-700";



  const inactiveClass =



    "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300";



  function select(mode: ViewMode) {



    if (mode !== value) {



      onChange(mode);



    }



  }



</script>



<div class={wrapperClass}>



  <button



    type="button"



    class={`${baseButtonClass} ${value === "grid" ? activeClass : inactiveClass}`}



    aria-pressed={value === "grid"}



    aria-label="Grid Weergave"



    on:click={() => select("grid")}



  >



    <svg



      xmlns="http://www.w3.org/2000/svg"



      viewBox="0 0 20 20"



      fill="currentColor"



      class={iconSizeClass}



      aria-hidden="true"



    >



      <path



        fill-rule="evenodd"



        d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z"



        clip-rule="evenodd"



      />



    </svg>



  </button>



  <button



    type="button"



    class={`${baseButtonClass} ${value === "list" ? activeClass : inactiveClass}`}



    aria-pressed={value === "list"}



    aria-label="Lijst Weergave"



    on:click={() => select("list")}



  >



    <svg



      xmlns="http://www.w3.org/2000/svg"



      viewBox="0 0 20 20"



      fill="currentColor"



      class={iconSizeClass}



      aria-hidden="true"



    >



      <path



        fill-rule="evenodd"



        d="M2 4.75A.75.75 0 0 1 2.75 4h14.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 4.75Zm0 5A.75.75 0 0 1 2.75 9h14.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 9.75Zm0 5A.75.75 0 0 1 2.75 14h14.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 14.75Z"



        clip-rule="evenodd"



      />



    </svg>



  </button>



</div>



